import os
import wget
import vk_api
import time
from tqdm import tqdm
import getpass


login = "login"
password = "password"

login = input("Type your VK login: ")
print("Login:",login)
password = getpass.getpass("Type your VK password: ")

destination_folder = input("Type the path to destination folder where the photos will be saved. Default value is /VK_photos/")
if not destination_folder:
    destination_folder = "VK_photos"

print("Destination folder:",destination_folder)

vk_session = vk_api.VkApi(login, password)
vk_session.auth()
vk = vk_session.get_api()


def get_urls(method, base, album_id = 0):
    photo_urls = []
    if album_id:
        photos = vk.photos.get(album_id=album_id)
    else:
        photos = method()
    for step in range(photos["count"]//base+1):
        if album_id:
            photos = vk.photos.get(album_id=album_id,offset = step*base, count = base)
        else:
            photos = method(offset = step*base, count = base)
        
        names = [x["sizes"] for x in photos["items"]]
        larges_urls = [url[-1]["url"] for url in names]
        photo_urls.extend(larges_urls)
    
    return photo_urls


photos_dict = {}

print ("Reading wall photos...")
photos_dict["Wall_photos"] = get_urls(vk.photos.getAll,100)

print ("Reading photos you're tagged on...")
photos_dict["Tagged_photos"]  = get_urls(vk.photos.getUserPhotos,100)

print ("Reading albums...")
albums = vk.photos.get_albums(count=100)
for album in albums["items"]:
    print ("Reading album",album["title"])
    photos_dict[album["title"]] = get_urls(vk.photos.get,100, album_id = album["id"])
    
for album in photos_dict:
    print ("Downloading album",album,"\n")
    if destination_folder:
        output_folder = os.path.join(destination_folder,album)
    else:
        output_folder = album
    if not os.path.isdir(output_folder):
        os.makedirs(output_folder)
    for image in tqdm(photos_dict[album]):
        wget.download(url = image,out = output_folder,bar=None)