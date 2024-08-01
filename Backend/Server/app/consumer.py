import os
import uuid
import asyncio
import aio_pika
import app.link_analysis.screenshot_maker as screenshot_maker


class AsyncRpcClient:
    def __init__(self, rpc_queue):
        self.rpc_queue = rpc_queue

    async def connect(self):
        self.connection = await aio_pika.connect_robust("amqp://guest:guest@localhost/")
        self.channel = await self.connection.channel()
        self.callback_queue = await self.channel.declare_queue(exclusive=True)
        await self.callback_queue.consume(self.on_response)

    async def on_response(self, message: aio_pika.IncomingMessage):
        async with message.process():
            if self.corr_id == message.correlation_id:
                self.response = message.body.decode()

    async def call(self, payload):
        self.response = None
        self.corr_id = str(uuid.uuid4())
        await self.channel.default_exchange.publish(
            aio_pika.Message(
                body=str(payload).encode(),
                correlation_id=self.corr_id,
                reply_to=self.callback_queue.name
            ),
            routing_key=self.rpc_queue,
        )
        while self.response is None:
            await asyncio.sleep(0.1)
        return self.response

    async def close(self):
        await self.connection.close()

async def analyze_message_rpc(message):
    rpc_client = AsyncRpcClient(rpc_queue='message_analysis_queue')
    await rpc_client.connect()
    try:
        response = await rpc_client.call(message)
        return response
    finally:
        await rpc_client.close()

async def analyze_link_rpc(link):
    print(f'Analyzing link: "{link}"')
    rpc_client = AsyncRpcClient(rpc_queue='link_analysis_queue')
    await rpc_client.connect()
    try:
        response = await rpc_client.call(link)
        return response
    finally:
        await rpc_client.close()

async def take_screenshot_rpc(url):
    print(f'Taking screenshot of: "{url}"')
    rpc_client = AsyncRpcClient(rpc_queue='screenshot_queue')
    await rpc_client.connect()
    try:
        screenshot_directory = os.path.join(os.getcwd(), 'public', 'screenshots')
        screenshot_name = await screenshot_maker.take_screenshot(url, screenshot_directory)
        if screenshot_name:
            screenshot_path = os.path.join(screenshot_directory, screenshot_name)
            print(f'Screenshot saved to: {screenshot_path}')
            return screenshot_name
        else:
            print(f'Failed to take screenshot for: "{url}"')
            return None
    except Exception as e:
        print(f"Error taking screenshot for {url}: {e}")
        return None
    finally:
        await rpc_client.close()
