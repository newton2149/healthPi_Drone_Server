import asyncio
import re
import requests
import asyncio
from mavsdk import System

class Message:
    def __init__(self,latitude,longitude):
        self.latitude = latitude
        self.longitude = longitude
        
        

def getLatestLaunchDirection():
    response = requests.get("http://localhost:8080/message/nextLaunch")
    msg = Message(response.json()["latitudeDeg"],response.json()["longitudeDeg"])
    return msg
  
async def run(latitude,longitude):

    drone = System()
    await drone.connect(system_address="udp://:14540")

    status_text_task = asyncio.ensure_future(print_status_text(drone))

    print("Waiting for drone to connect...")
    async for state in drone.core.connection_state():
        if state.is_connected:
            print(f"-- Connected to drone!")
            break

    print("Waiting for drone to have a global position estimate...")
    async for health in drone.telemetry.health():
        if health.is_global_position_ok and health.is_home_position_ok:
            print("-- Global position estimate OK")
            break

    print("-- Arming")
    await drone.action.arm()

    print("-- Taking off")
    await drone.action.takeoff()

    await drone.action.goto_location(110,110,100,20)
    drone.action.return_to_launch()
    

    # await asyncio.sleep(10)
    

    print("-- Landing")
    # await drone.action.return_to_launch()


    status_text_task.cancel()

async def print_status_text(drone):
    try:
        async for status_text in drone.telemetry.status_text():
            print(f"Status: {status_text.type}: {status_text.text}")
    except asyncio.CancelledError:
        return



if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    print("Launch Server Has Been Initated")
    while True:
        print("1.Launch the drone")
        print("2.Exit")
        x = int(input("Enter the option"))
        if x==1:
            msg = getLatestLaunchDirection()
            loop.run_until_complete(run(msg.latitude,msg.longitude))
        else:
            break

    print("Launch Server Ended")

