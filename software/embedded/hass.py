import sys

is_micropython = sys.implementation.name == 'micropython'

import socket
import select

import asyncio
import json

from namespace import Namespace

SSDP_PORT = 1900

_SSDP_HEADER = b"""M-SEARCH * HTTP/1.1\r
HOST:239.255.255.250:1900\r
MAN:"ssdp:discover"\r
ST:ssdp:all\r
MX:3\r
\r
"""


class HomeAssistant:
    """Home Assistant REST client with SSDP discovery and a keep-alive HTTP session."""

    def __init__(self, config, secrets, network_ready=None, verbose=True):
        """
        Parameters:
            config: ``Namespace`` with optional ``hass_host``, ``hass_port``.
            secrets: ``Namespace`` with ``hass_api_token`` (long-lived access token).
            network_ready: ``asyncio.Event`` set while WiFi (or LAN) is up (from ``EEMON42``).
            verbose: print discovery and HTTP debug lines.
        """
        self.config = config
        self.secrets = secrets
        self.network_ready = network_ready
        self.verbose = verbose

        self._host = secrets.get('hass_host')
        self._port = int(secrets.get('hass_port', 8123))
        self._token = secrets.get('hass_api_token', '')

        self._reader = None
        self._writer = None
        self._lock = asyncio.Lock()
        self.hass_ready = asyncio.Event()

    def _log(self, *args):
        if self.verbose:
            print(*args)

    async def discover(self, rounds=20):
        """Locate Home Assistant via SSDP. Returns IP string or ``None``."""
        mcast = socket.getaddrinfo('239.255.255.250', SSDP_PORT)[0][-1]
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        if is_micropython:
            sock.bind(socket.getaddrinfo('0.0.0.0', 0)[0][-1])
        else:
            sock.bind(('0.0.0.0', 0))

        poll = select.poll()
        poll.register(sock, select.POLLIN)
        try:
            for _ in range(rounds):
                self._log('SSDP discover…')
                sock.sendto(_SSDP_HEADER, mcast)
                for _ in range(10):
                    for fd, event, *_ in poll.poll(0):
                        try:
                            data, addr = sock.recvfrom(1000)
                            if data and b'HomeAssistant' in data:
                                return addr[0]
                        except OSError:
                            break
                    await asyncio.sleep(0.1)
        finally:
            poll.unregister(sock)
            sock.close()
        return None

    async def _resolve_host(self):
        if self._host:
            return self._host
        ip = await self.discover()
        if ip:
            self._host = ip
            print(f'Home Assistant discovered at {ip}')
            self._log(f'Home Assistant discovered at {ip}')
        return self._host

    async def _disconnect(self):
        self.hass_ready.clear()
        w = self._writer
        self._reader = None
        self._writer = None
        if w is None:
            return
        try:
            if is_micropython:
                await w.aclose()
            else:
                w.close()
                await w.wait_closed()
        except OSError:
            pass

    async def _connect(self):
        host = await self._resolve_host()
        if not host:
            raise OSError('Home Assistant host unknown')
        self._reader, self._writer = await asyncio.open_connection(host, self._port)
        self.hass_ready.set()
        print(f'Home Assistant connected to {host}:{self._port}')
        self._log(f'Connected to Home Assistant at {host}:{self._port}')

    def _connected(self):
        return self._reader is not None and self._writer is not None

    async def _write(self, data):
        if is_micropython:
            await self._writer.awrite(data)
        else:
            self._writer.write(data)
            await self._writer.drain()

    async def _readline(self):
        return await self._reader.readline()

    async def _readexactly(self, n):
        if is_micropython:
            return await self._reader.readexactly(n)
        data = b''
        while len(data) < n:
            chunk = await self._reader.read(n - len(data))
            if not chunk:
                raise OSError('Connection closed while reading response body')
            data += chunk
        return data

    async def _read_response_body(self, headers):
        length = None
        for line in headers:
            if line.lower().startswith(b'content-length:'):
                length = int(line.split(b':', 1)[1].strip())
                break
        if length is not None:
            return await self._readexactly(length)
        return await self._reader.read(-1)

    async def _request(self, method, path, body=None):
        """Send one HTTP/1.1 request on the keep-alive connection."""
        host_hdr = f'{self._host}:{self._port}'
        header_lines = [
            f'{method} {path} HTTP/1.1',
            f'Host: {host_hdr}',
            'Connection: keep-alive',
            'User-Agent: EEMON42',
            f'Authorization: Bearer {self._token}',
        ]
        payload = b''
        if body is not None:
            payload = json.dumps(body).encode('utf-8')
            header_lines.append('Content-Type: application/json')
            header_lines.append(f'Content-Length: {len(payload)}')
        msg = '\r\n'.join(header_lines).encode('latin-1') + b'\r\n\r\n' + payload
        await self._write(msg)

        status_line = await self._readline()
        if not status_line:
            raise OSError('Empty response from Home Assistant')
        parts = status_line.split(None, 2)
        if len(parts) < 2:
            raise OSError(f'Invalid HTTP response: {status_line!r}')
        status = int(parts[1])

        resp_headers = []
        while True:
            line = await self._readline()
            if line == b'\r\n' or not line:
                break
            resp_headers.append(line.rstrip(b'\r\n'))

        resp = await self._read_response_body(resp_headers)
        if status != 200:
            raise OSError(f'Home Assistant HTTP {status}: {resp[:200]!r}')
        if not resp:
            return None
        return Namespace(json.loads(resp))

    async def _call(self, method, path, body=None):
        await self.hass_ready.wait()
        async with self._lock:
            try:
                return await self._request(method, path, body)
            except OSError:
                await self._disconnect()
                raise

    async def set_state(self, entity_id, state, attributes=None):
        """POST entity state (called from EMON / telemetry tasks)."""
        body = {'state': state}
        if attributes is not None:
            body['attributes'] = attributes
        try:
            result = await self._call('POST', f'/api/states/{entity_id}', body)
            self._log(f'set_state {entity_id} -> {state}')
            return result
        except OSError as e:
            print(f'Home Assistant set_state {entity_id} failed: {e!r}')
            raise

    async def get_state(self, entity_id):
        """GET entity state."""
        try:
            return await self._call('GET', f'/api/states/{entity_id}')
        except OSError as e:
            print(f'Home Assistant get_state {entity_id} failed: {e!r}')
            raise

    async def run(self):
        """Background task: wait for network, discover HA if needed, keep session open."""
        if self.network_ready is None:
            raise ValueError('network_ready event is required')

        if self._host:
            print(f'Home Assistant connection task using {self._host}:{self._port}')
        else:
            print('Home Assistant connection task (host from SSDP when WiFi is up)')
        try:
            while True:
                await self.network_ready.wait()
                while self.network_ready.is_set():
                    if not self._host:
                        await self._resolve_host()
                        if not self._host:
                            self._log('Home Assistant host unknown, retrying discovery…')
                            await asyncio.sleep(5)
                            continue

                    try:
                        async with self._lock:
                            if not self._connected():
                                await self._disconnect()
                                await self._connect()
                        await asyncio.sleep(1)
                    except OSError as e:
                        print(f'Home Assistant connection error: {e!r}')
                        self._log(f'Home Assistant connection error: {e!r}')
                        async with self._lock:
                            await self._disconnect()
                        await asyncio.sleep(5)
                async with self._lock:
                    await self._disconnect()
        except asyncio.CancelledError:
            raise
        finally:
            async with self._lock:
                await self._disconnect()
            print('Home Assistant connection task stopped')
