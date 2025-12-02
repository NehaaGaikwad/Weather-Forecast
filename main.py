from tkinter import *
import tkinter as tk
import pytz
from geopy.geocoders import Nominatim
from datetime import datetime
import requests
from PIL import Image, ImageTk
from tkinter import messagebox
from timezonefinderL import TimezoneFinder
from dotenv import load_dotenv
import os

load_dotenv()

# Main Window Setup
root = Tk()
root.title("Weather Forecast")
root.geometry("750x470+300+200")
root.resizable(False, False)
root.config(bg="#202731")

# Function to Fetch and Display Weather
def getWeather():
    try:
        city = textfield.get()
        if not city:
            messagebox.showerror("Error", "Please enter a city name.")
            return

        # 1. Geocoding and Timezone
        geolocator = Nominatim(user_agent="new")
        location = geolocator.geocode(city)
        if not location:
            messagebox.showerror("Error", "City not found.")
            return
            
        obj = TimezoneFinder()
        result = obj.timezone_at(lat=location.latitude, lng=location.longitude)
        
        timezone.config(text=result)
        long_lat.config(text=f"{round(location.latitude,4)}°N {round(location.longitude,4)}°E")

        home = pytz.timezone(result)
        local_time = datetime.now(home)
        current_time = local_time.strftime("%I:%M %p")
        clock.config(text=current_time)

        # 2. Fetch Weather Data 
        api_key = os.getenv('API_KEY')
        api = f"https://api.openweathermap.org/data/2.5/forecast?q={city}&appid={api_key}&units=metric"
        json_data = requests.get(api).json()

        if json_data.get("cod") != "200":
            messagebox.showerror("API Error", f"Could not retrieve data for {city}. Check city name or API status.")
            return

        # 3. Current Weather (Displayed on the left side, always the first entry)
        current = json_data['list'][0]
        temp = current['main']['temp']
        pressure = current['main']['pressure']
        wind_speed = current['wind']['speed']
        description = current['weather'][0]['description']

        t.config(text=f"{temp}°C")
        p.config(text=f"{pressure}hpa")
        w.config(text=f"{wind_speed}m/s")
        d.config(text=f"{description}")

        # 4. Daily Forecast - Pick one entry per day for the 5 forecast boxes
        
        # Get today's date in the target timezone
        today_date_str = datetime.now(home).strftime('%Y-%m-%d')
        
        # List to hold the 5 forecast entries starting from TOMORROW
        daily_data = []
        
        # Set of dates already included (start by excluding today)
        seen_dates = {today_date_str} 
        
        # Iterate through the forecast data to get 5 unique, upcoming days starting from TOMORROW
        for entry in json_data['list']:
            date_str = entry['dt_txt'].split()[0]  # Get YYYY-MM-DD
            
            # Check if this date has not been seen yet
            if date_str not in seen_dates:
                # This must be the first entry for a new day (starting from tomorrow)
                daily_data.append(entry)
                seen_dates.add(date_str) # Mark this date as seen
            
            # Stop once we have 5 days 
            if len(daily_data) == 5:
                break
        
        global icons 
        icons = []
        temps = []

        for idx in range(len(daily_data)):
            entry = daily_data[idx]
            weather_list = entry.get('weather', [])
            if weather_list:
                icon_code = weather_list[0].get('icon', '01d')
                
                try:
                    img = Image.open(f"icon/{icon_code}@2x.png").resize((50, 50))
                    icons.append(ImageTk.PhotoImage(img))
                except FileNotFoundError:
                    print(f"Warning: Icon file not found for {icon_code}")
                    icons.append(None) 
                    
                # Store Max Temp (day) and Feels Like (night/approx)
                temps.append((entry['main']['temp_max'], entry['main']['feels_like'])) 

        # 5. Update Forecast Widgets
        day_widget = [
            (firstimage, day1, day1temp),
            (secondimage, day2, day2temp),
            (thirdimage, day3, day3temp),
            (fourthimage, day4, day4temp),
            (fifthimage, day5, day5temp),
        ]

        # Reset all labels first
        for img_label, day_label, temp_label in day_widget:
            img_label.config(image="")
            img_label.image = None
            day_label.config(text="---")
            temp_label.config(text="Day: --\nNight: --")


        for i, (img_label, day_label, temp_label) in enumerate(day_widget):
            if i < len(icons):
                # Update Icon and Temp
                if icons[i] is not None:
                    img_label.config(image=icons[i])
                    img_label.image = icons[i]
                
                temp_label.config(text=f"Day: {temps[i][0]:.1f}°C\nNight: {temps[i][1]:.1f}°C") # Added formatting to temps
                
                # Get the actual day name from the forecast entry date
                dt_object = datetime.strptime(daily_data[i]['dt_txt'], '%Y-%m-%d %H:%M:%S')
                day_label.config(text=dt_object.strftime("%A")) 

            else:
                day_label.config(text="---")
                temp_label.config(text="Day: --\nNight: --")
                img_label.config(image="")


    except Exception as e:
        print(f"An error occurred: {e}")
        messagebox.showerror("Error", f"Could not fetch weather data. Error details: {e}")

# GUI Elements Setup

## Icon
try:
    image_icon = PhotoImage(file="Images/logo.png")
    root.iconphoto(False, image_icon)
except:
    pass 

Round_box = PhotoImage(file="Images/Rounded Rectangle 1.png")
Label(root, image=Round_box, bg="#202731").place(x=30, y=60)

# Labels for Current Weather data titles
Label1 = Label(root, text="Temperature", font=("Helvetica", 13 ,"bold"), fg="#323661", bg="#aad1c8")
Label1.place(x=50, y=140)

Label3 = Label(root, text="Pressure", font=("Helvetica", 13 ,"bold" ,"bold"), fg="#323661", bg="#aad1c8")
Label3.place(x=50, y=160)

Label4 = Label(root, text="Wind Speed", font=("Helvetica", 13 ,"bold"), fg="#323661", bg="#aad1c8")
Label4.place(x=50, y=180)

Label5 = Label(root, text="Description", font=("Helvetica", 13 ,"bold"), fg="#323661", bg="#aad1c8")
Label5.place(x=50, y=200)

# Search Box
Search_image = PhotoImage(file="Images/Rounded Rectangle 3.png")
myimage = Label(root, image=Search_image, bg="#202731")
myimage.place(x=270, y=122)

weat_image = PhotoImage(file="Images/Layer 7.png")
weatherimage = Label(root, image=weat_image, bg="#333c4c")
weatherimage.place(x=290, y=127)

textfield = tk.Entry(root, justify="center", width=15, font=("poppins", 25, "bold"), bg="#333c4c", border=0, fg="white")
textfield.place(x=370, y=130)

Search_icon = PhotoImage(file="Images/Layer 6.png")
myimage_icon = Button(root, image=Search_icon, borderwidth=0, cursor="hand2", bg="#333c4c", command=getWeather)
myimage_icon.place(x=640, y=135)

# Bottom box 
frame = Frame(root, width=900, height=180, bg="#7094d4")
frame.pack(side=BOTTOM)

# Boxes on the bottom frame 
firstbox = PhotoImage(file="Images/Rounded Rectangle 2.png")
secondbox = PhotoImage(file="Images/Rounded Rectangle 2 copy.png") 

# BACKGROUND IMAGE (First Box Only)
Label(frame, image=firstbox, bg="#7094d4").place(x=30, y=20)

# Clock and Location Labels
clock = Label(root, font=("Helvetica", 20 ,"bold"), bg="#202731", fg="white")
clock.place(x=30, y=20)

timezone = Label(root, font=("Helvetica", 20 ,"bold"), bg="#202731", fg="white")
timezone.place(x=500, y=20)

long_lat = Label(root, font=("Helvetica", 12 ,"bold"), bg="#202731", fg="white")
long_lat.place(x=500, y=60)

# Current weather data labels 
t = Label(root, font=("Helvetic", 12, "bold"), bg="#aad1c8", fg="#323661") 
t.place(x=160, y=140)

p = Label(root, font=("Helvetic", 12, "bold"), bg="#aad1c8", fg="#323661") 
p.place(x=160, y=160)

w = Label(root, font=("Helvetic", 12, "bold"), bg="#aad1c8", fg="#323661") 
w.place(x=160, y=180)

d = Label(root, font=("Helvetic", 12, "bold"), bg="#aad1c8", fg="#323661") 
d.place(x=160, y=200)

# Forecast Frames

# First cell (Large Forecast Box) - Current Day/Time
firstframe = Frame(frame, width=230, height=132, bg="#323661")
firstframe.place(x=35, y=30) 

firstimage = Label(firstframe, bg="#323661")
firstimage.place(x=15, y=30)

# day1 - Centered and Bold
day1 = Label(firstframe, font=("arial", 20, "bold"), bg="#323661", fg="white", anchor="center") 
day1.place(x=75, y=5)

day1temp = Label(firstframe, font=("arial", 14, "bold"), bg="#323661", fg="white", justify=LEFT) 
day1temp.place(x=75, y=65)

# Second cell (Day 2)
secondframe = Frame(frame, width=90, height=115, bg="#eeefea")
secondframe.place(x=300, y=30) 

secondimage = Label(secondframe, bg="#eeefea")
secondimage.place(x=20, y=10) 

# day2 
day2 = Label(secondframe, bg="#eeefea", fg="#000", font=("arial", 11, "bold"), anchor="center") 
day2.place(x=5, y=60) 

day2temp = Label(secondframe, bg="#eeefea", fg="#000", font=("arial", 8, "bold"), justify=CENTER) 
day2temp.place(x=10, y=80) 

# Third cell (Day 3) 
thirdframe = Frame(frame, width=90, height=115, bg="#eeefea") 
thirdframe.place(x=400, y=30) 

thirdimage = Label(thirdframe, bg="#eeefea")
thirdimage.place(x=20, y=10) 

# day3 
day3 = Label(thirdframe, bg="#eeefea", fg="#000", font=("arial", 11, "bold"), anchor="center") 
day3.place(x=5, y=60) 

day3temp = Label(thirdframe, bg="#eeefea", fg="#000", font=("arial", 8, "bold"), justify=CENTER)
day3temp.place(x=10, y=80) 

# Fourth cell (Day 4)
fourthframe = Frame(frame, width=90, height=115, bg="#eeefea")
fourthframe.place(x=500, y=30) 

fourthimage = Label(fourthframe, bg="#eeefea")
fourthimage.place(x=20, y=10) 

# day4 
day4 = Label(fourthframe, bg="#eeefea", fg="#000", font=("arial", 11, "bold"), anchor="center") 
day4.place(x=5, y=60) 

day4temp = Label(fourthframe, bg="#eeefea", fg="#000", font=("arial", 8, "bold"), justify=CENTER) 
day4temp.place(x=10, y=80) 

# Fifth cell (Day 5)
fifthframe = Frame(frame, width=90, height=115, bg="#eaecef")
fifthframe.place(x=600, y=30) 

fifthimage = Label(fifthframe, bg="#eeefea")
fifthimage.place(x=20, y=10) 

# day5 
day5 = Label(fifthframe, bg="#eeefea", fg="#000", font=("arial", 11, "bold"), anchor="center") 
day5.place(x=5, y=60) 

day5temp = Label(fifthframe, bg="#eeefea", fg="#000", font=("arial", 8, "bold"), justify=CENTER)
day5temp.place(x=10, y=80) 


root.mainloop()