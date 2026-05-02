from channels.generic.websocket import AsyncWebsocketConsumer
import json
from asgiref.sync import sync_to_async
from .models import UserProfile


class DashboardConsumer(AsyncWebsocketConsumer):

    async def connect(self):

        user = self.scope["user"]

        if not user.is_authenticated:
            await self.close()
            return

        # 🔥 profile fetch
        profile = await sync_to_async(UserProfile.objects.get)(user=user)

        clinic_id = profile.clinic_id

        # 🔥 ROLE BASED GROUP
        if profile.role == "receptionist":

            self.group_name = f"dashboard_{clinic_id}_receptionist"

        elif profile.role == "assistant":

            if profile.assigned_doctor_id:
                self.group_name = f"dashboard_{clinic_id}_doctor_{profile.assigned_doctor_id}"
            else:
                await self.close()
                return

        else:  # doctor / owner

            self.group_name = f"dashboard_{clinic_id}_doctor_{profile.id}"

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
