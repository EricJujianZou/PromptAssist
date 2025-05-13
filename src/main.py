import sys
from PySide6.QtWidgets import QApplication
from .core.application import Application # Updated import

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(False)  # app runs without window
    
    # Initialize and run the main application logic from core.application
    snippet_app = Application() 
    
    sys.exit(app.exec())
    


            



# """ 
# * UIA PART - COMMENTED OUT
# """

# """ Initialize UIA polling for text content verification """
# def _init_uia_polling(self):
#     self.poll_timer = QTimer()
#     self.poll_timer.timeout.connect(self._verify_buffer_with_uia)

#     #base polling rate of 500ms, should only use around 3-5% CPU if performing buffer check
#     self.polling_interval = 500
#     self.poll_timer.start(self.polling_interval)



# """ Poll the active text field and verify buffer """
# def _verify_buffer_with_uia(self):
#     if not self._should_perform_uia_check():
#         return    
#     try:
#         # Get the text from the active control
#         text = self._get_text_from_focused_control()
#         # print("Buffer: '{}'".format(self.buffer)) # Optional debug
#         # print("UIA text: '{}'".format(text[:50] if text else "")) # Optional debug

#         # Early exit if no text
#         if not text:
#             # self.buffer = "" # Maybe don't clear buffer if UIA fails?
#             return
        
#         # Buffer comparison
#         if self.buffer and not text.endswith(self.buffer):
#             print("Buffer doesn't match UIA text, resetting buffer")
#             self.buffer = ""

#     except Exception as e:
#         # UIA access failed
#         print(f"UIA verification failed: {e}")

#     # Adjust polling rate based on typing activity
#     self._adjust_polling_rate()

# """ Adjust the polling rate if the user is typing or not """
# def _adjust_polling_rate(self):
#     time_since_input = time.time() - self.last_input_time

#     if time_since_input < 2.0: #They're typing. 2 second window accounts for slow typers
#         if self.polling_interval != 100:
#             self.polling_interval = 100
#             self.poll_timer.setInterval(self.polling_interval)
#     else: #They're not typing
#         if self.polling_interval != 500:
#             self.polling_interval = 500
#             self.poll_timer.setInterval(self.polling_interval)

# """ Check if we should do UIA check """
# def _should_perform_uia_check(self):
#     #Skip if the buffer is empty (they not typing) and no recent activity
#     # if not self.buffer and (time.time() - self.last_input_time) > 2.0:
#     #     return False

#     #Skip if the active window is blacklisted
#     current_app = self._get_current_app_name() #not use active app cus blacklisted is blacklisted regardless of which window is active
#     if current_app in self.blacklisted_apps:
#         return False

#     return True # Simplified for now if UIA is minimal

# """ Get the text from the focused control """
# def _get_text_from_focused_control(self):
#     """Get text from the currently focused control with improved focus detection"""
#     # THIS ENTIRE METHOD IS COMMENTED OUT AS UIA IS DISABLED
#     return "" # Return empty string if UIA is disabled

# """ Check if the cached control is still valid, or if the user closed the window or modified UI """
# def _is_control_valid(self):
#     # THIS ENTIRE METHOD IS COMMENTED OUT AS UIA IS DISABLED
#     return False # Assume invalid if UIA is disabled
        

    


    

    
