from channels.generic.websocket import AsyncWebsocketConsumer
import json

class DashboardConsumer(AsyncWebsocketConsumer):

    async def connect(self):

        # 🔥 URL se clinic_id lo
        self.clinic_id = self.scope["url_route"]["kwargs"]["clinic_id"]

        # 🔥 unique group per clinic
        self.group_name = f"dashboard_{self.clinic_id}"

        await self.channel_layer.group_add(
            self.group_name,
            self.channel_name
        )

        await self.accept()


    async def disconnect(self, close_code):

        await self.channel_layer.group_discard(
            self.group_name,
            self.channel_name
        )


    async def send_update(self, event):

        await self.send(text_data=json.dumps({
            "type": "send_update",
            "data": event["data"]
        }))
