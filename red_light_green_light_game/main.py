import cv2
import tkinter as tk
from threading import Thread
import time
import numpy as np


class LightGame:
    TIMER_DURATION = 5  # Change the timer value based on your preference

    def __init__(self, root):
        self.root = root
        self.root.title("Red Light Green Light Game")
        self.root.geometry("300x300")
        
        self.canvas = tk.Canvas(self.root, width=300, height=300, bg="white")
        self.canvas.pack()
        
        self.current_light = "Red"
        self.game_running = True
        self.timer_value = self.TIMER_DURATION  # Use the class-level constant
        
        self.light_indicator = self.canvas.create_oval(100, 100, 200, 200, fill="red")
        self.timer_text = self.canvas.create_text(150, 250, text=f"Time: {self.timer_value}s", font=("Arial", 16), fill="black")
        
        self.webcam_thread = Thread(target=self.check_motion, daemon=True)
        self.webcam_thread.start()
        
        self.toggle_light()
        self.update_timer()

    def toggle_light(self):
        if not self.game_running:
            return
        
        # Toggle light color
        if self.current_light == "Red":
            self.current_light = "Green"
            self.canvas.itemconfig(self.light_indicator, fill="green")
        else:
            self.current_light = "Red"
            self.canvas.itemconfig(self.light_indicator, fill="red")
        
        # Reset the timer every light change
        self.timer_value = self.TIMER_DURATION
        self.root.after(self.TIMER_DURATION * 1000, self.toggle_light)

    def update_timer(self):
        if not self.game_running:
            return
        
        self.canvas.itemconfig(self.timer_text, text=f"Time: {self.timer_value}s")
        self.timer_value -= 1
        
        # Update the timer every second and ensure it syncs with light toggle
        if self.timer_value >= 0:
            self.root.after(1000, self.update_timer)

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

    def end_game(self):
        self.game_running = False
        self.canvas.create_text(150, 150, text="Game Over!", font=("Arial", 24), fill="black")
        self.root.after(500, self.root.destroy)


if __name__ == "__main__":
    root = tk.Tk()
    game = LightGame(root)
    root.mainloop()