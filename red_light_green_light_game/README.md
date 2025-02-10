## [Build your own Red Light Green Light Game with Python](https://anytool.in/blog/post/build-your-own-red-light-green-light-with-python/)

The game uses your laptop/PC webcam to detect motion. You are allowed to move when the green light is 
shown, but you should freeze when the red light is shown. If any movement is detected when there is a 
red light, then the game ends. Green light and red light appear alternatively at fixed intervals. In 
this tutorial, we are using five seconds as the interval.

## Setting up a virtual environment and installing packages

In your code editor, open the terminal and create a virtual environment and activate it to install 
dependencies.

```astro
python -m venv venv
cd venv/Scripts
activate
cd ../..
```

Now, after activating the virtual environment, we can install the necessary Python packages. 
**cv2:** OpenCV is used for video capture and motion detection.
**numpy:** For efficient numerical operations in OpenCV
Now run the below in your terminal to install the dependencies.

```astro
pip install numpy opencv-python
```

## Importing packages

With the environment setup and packages installed, it is time for us to get into coding mode.

```astro title="src/components/DynamicAttributes.astro" "{name}" "${name}"
import cv2
import tkinter as tk
from threading import Thread
import time
import numpy as np
```
<ul>
<li>cv2: OpenCV is used for video capture and motion detection.</li>
<li>tkinter: Used to create the graphical user interface (GUI) for the game.</li>
<li>threading: Enables running tasks (motion detection and GUI) concurrently.</li>
<li>time: For managing delays and timing tasks.</li>
<li>numpy: For efficient numerical operations in OpenCV.</li>
</ul>

## Initializing the Game
Next we initiate the logic class. The LightGame class encapsulates the game logic. The TIMER_DURATION class-level constant specifies 
the duration for each red or green light. Next we will setup the contructor.

```astro title="src/components/DynamicHtml.astro" "{item}"
class LightGame:
    TIMER_DURATION = 5
    def __init__(self, root):
	self.root = root
	self.root.title("Red Light Green Light Game")
	self.root.geometry("300x300")
```
<ul>
<li>self.root: This is the main UI Tkinter window.</li>
<li>self.root.title and self.root.geometry: Sets the window title and size.</li>
</ul>

We leave it to you to experiment with Tkinter window styling and properties.

```astro title="src/components/ConditionalHtml.astro" "visible"
self.canvas = tk.Canvas(self.root, width=300, height=300, bg="white")
self.canvas.pack()
self.light_indicator = self.canvas.create_oval(100, 100, 200, 200, fill="red")
self.timer_text = self.canvas.create_text(150, 250, text=f"Time: {self.timer_value}s", font=("Arial", 16), fill="black")
```

We have now added the UI elements,and it is self explanatory. Next we are initlializing some variables 
that track the current game status.

```astro title="src/components/ConditionalHtml.astro" "visible"
self.current_light = "Red"
self.game_running = True
self.timer_value = self.TIMER_DURATION
```
Now, some important part. We are running the camera input for motion detection and the UI in separate 
threads.

```astro title="src/components/ConditionalHtml.astro" "visible"
self.webcam_thread = Thread(target=self.check_motion, daemon=True)
self.webcam_thread.start()
```

self.webcam_thread performs the motion detection in a separate thread without interfering the UI. Post 
this game logic recursive functions are called
```astro title="src/components/ConditionalHtml.astro" "visible"
self.toggle_light()
self.update_timer()
```

## Toggle Light

The toggle_light is responsible for changing the colour of light at regular intervals. It takes the current 
colour to update the UI with other colour

```astro title="src/components/ConditionalHtml.astro" "visible"
def toggle_light(self):
    if not self.game_running:
        return
	if self.current_light == "Red":
        self.current_light = "Green"
        self.canvas.itemconfig(self.light_indicator, fill="green")
    else:
        self.current_light = "Red"
        self.canvas.itemconfig(self.light_indicator, fill="red")
	self.timer_value = self.TIMER_DURATION
    self.root.after(self.TIMER_DURATION * 1000, self.toggle_light)
```
self.root.after, schedules the next toggle after 5 seconds. Note Python timer works in milliseconds so we 
do a *1000.

## Timer Update

The update_timer function is responsible for updating the timer in the UI.

```astro title="src/components/ConditionalHtml.astro" "visible"
def update_timer(self):
    if not self.game_running:
        return
	self.canvas.itemconfig(self.timer_text, text=f"Time: {self.timer_value}s")
    self.timer_value -= 1
	if self.timer_value >= 0:
        self.root.after(1000, self.update_timer)
```
The update_timer function is called again after 1 second if the timer value is not below 0. The timer 
text is updated on the canvas. The timer value is decremented by 1.

## Motion Detection

Now comes the key part; Motion Detection.

```astro title="src/components/ConditionalHtml.astro" "visible"
    def check_motion(self):
        cap = cv2.VideoCapture(0)
        _, frame1 = cap.read()
        _, frame2 = cap.read()

        # Define the minimum contour area for motion detection
		# Adjust this value for sensitivity. Lower the value, higher the sensitivity
        MIN_CONTOUR_AREA = 1000
        
        while self.game_running:
            if self.current_light == "Red":
                diff = cv2.absdiff(frame1, frame2)
                gray = cv2.cvtColor(diff, cv2.COLOR_BGR2GRAY)
                blur = cv2.GaussianBlur(gray, (5, 5), 0)
                _, thresh = cv2.threshold(blur, 20, 255, cv2.THRESH_BINARY)
                dilated = cv2.dilate(thresh, None, iterations=3)
                contours, _ = cv2.findContours(dilated, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

                for contour in contours:
                    if cv2.contourArea(contour) > MIN_CONTOUR_AREA:
                        self.end_game()
                        break
            
            frame1 = frame2
            _, frame2 = cap.read()

            # Display the live video feed
            cv2.imshow("Live Video Feed", frame2)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                self.end_game()
                break

        cap.release()
        cv2.destroyAllWindows()
```
<ul>
<li>cv2.VideoCapture: Opens webcam for motion detection.</li>
<li>_, frame1 = cap.read() and _, frame2 = cap.read(): Captures two consecutive frames to detect differences.</li>
<li>cv2.absdiff: Computes the absolute difference between two frames.</li>
<li>cv2.cvtColor: Converts the result to grayscale.</li>
<li>cv2.GaussianBlur: Smoothens the image to reduce noise.</li>
<li>cv2.threshold: Creates a binary image for easier contour detection.</li>
<li>cv2.dilate: Enhances the white regions (motion areas).</li>
<li>cv2.findContours: Detects contours in the image.</li>
</ul>

If a contour's area exceeds the MIN_CONTOUR_AREA threshold during a red light, the game ends. The logic 
behind using of contour area works likea find n differences between two images. Here, the two images are 
the two frames, and the difference is caused motion. cv2.imshow() displays the camera feed which you'll 
generally see in any other OpenCV application. The game ends either through motion detection during red 
light or by pressing 'q'. It calls the end_game() function.

## Ending the Game

```astro title="src/components/ConditionalHtml.astro" "visible"
def end_game(self):
    self.game_running = False
    self.canvas.create_text(150, 150, text="Game Over!", font=("Arial", 24), fill="black")
    self.root.after(500, self.root.destroy)
```

The end_game function sets the game_running status variable to False, displays "Game Over!", and closes 
the Tkinter UI window.

## Main Execution
```astro title="src/components/ConditionalHtml.astro" "visible"
if __name__ == "__main__":
    root = tk.Tk()
    game = LightGame(root)
    root.mainloop()
```

The main function as you all might know, initiates the Tkinter UI window, and also calls the LightGame 
class constructor to start the game.


Until we meet you next time with another interesting project, happy coding guys!!
