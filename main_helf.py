from patchright.async_api import async_playwright, Page
from utils.humanizer import *
from utils.main_utils import *

import requests
import asyncio
import random

proxy = '172.232.204.189:24540:modeler_71tcGy:gbeh8dBfR3cY'



        
        
        

class Engine():
    def __init__(self, page):
        self.last_coords = random.choice([(0, random.randint(0, 500)), (random.randint(0, 500), 0)])
        self.page = page
        
    async def exists(self, xpath):
        try:
            if await self.page.is_visible(xpath):
                return True
        except Exception:
            return False
        
        
    async def human_type(self, text, xpath):
        
        await self.click(xpath)
        await asyncio.sleep(random.uniform(1, 1.5))

        for char in text:
            await self.page.keyboard.down(char)
            await asyncio.sleep(0.01, 0.02)
            await self.page.keyboard.up(char)
            await asyncio.sleep(0.09, 0.13)

        await asyncio.sleep(random.uniform(1, 1.5))
        
        
    
    async def click(self, xpath):
        while True:
            element = await self.page.wait_for_selector(xpath) 

            await element.scroll_into_view_if_needed()

            bounding_box = await element.bounding_box()

            if bounding_box:
                x = bounding_box['x']
                y = bounding_box['y']


                center_width = bounding_box['width'] / 2
                center_height = bounding_box['height'] / 2
                new_x = bounding_box['x'] + center_width
                new_y = bounding_box['y'] + center_height

                trajectory = HumanizeMouseTrajectory(self.last_coords, (new_x, new_y))

                points = trajectory.get_points()

                for i in range(0, len(points), 2):
                    await self.page.mouse.move(points[i], points[i+1])
                self.last_coords = (points[i], points[i+1])
                
                bounding_box = await element.bounding_box()
                if bounding_box:
                    if not bounding_box['x'] == x or not bounding_box['y'] == y:
                        continue
                
                try:
                    await self.page.click(xpath, position={'x': center_width, 'y': center_height})
                    break
                except Exception as e:
                    raise Exception('Ошибка во время клика', e)
                    
                    

class Youtube_Uploader():
    def __init__(self, proxy, g_login, g_password, g_recovery):
        self.engine = None
        
        self.proxy = proxy
        self.google_login = g_login
        self.google_password = g_password
        self.google_recovery = g_recovery
        
    async def start_automation(self):
        port = Vision(self.proxy).start_browser()
        
        async with async_playwright() as p:
            browser = await p.chromium.connect_over_cdp(endpoint_url=f'http://127.0.0.1:{port}')
            self.context = browser.contexts[0]
            self.page = await self.context.new_page()
            self.engine = Engine(self.page)
            await self.authorize()
            
            
            
            
            
    async def authorize(self):
        try:
            await self.page.goto('https://accounts.google.com/login')
            await self.engine.human_type(self.google_login, '//input[@type="email"]')
            await self.engine.click('//div[@id="identifierNext"]') 
            await self.engine.human_type(self.google_password, '//input[@type="password"]')
            await self.engine.click('//div[@id="passwordNext"]') 
            while True:
                    if await self.engine.exists('(//*[@data-action="selectchallenge"])[3]'):
                        await self.engine.click('(//*[@data-action="selectchallenge"])[3]')
                        await self.engine.human_type(self.google_recovery, '//input')
                        

                    if await self.engine.exists('(//*[@data-viewer-email]//button)[2]'):
                        await self.engine.click('(//*[@data-viewer-email]//button)[2]')
                        break


            await asyncio.sleep(5)
        except Exception as e:
            raise Exception('Ошибка при авторизации', e)




def get_google():
    with open('google.txt', 'r+') as txt:
        lines = txt.readlines()
        account = lines[0]
        email, password, recovery = account.split(':')
        txt.seek(0)
        txt.writelines(lines[1:])
        txt.truncate()
        return email, password, recovery



            
        
if __name__ == "__main__":
    try:
        email, password, recovery = get_google()
        uploader = Youtube_Uploader(proxy, email, password, recovery)
        asyncio.run(uploader.start_automation())
    except Exception as e:
        output(e, "RED")

        
    