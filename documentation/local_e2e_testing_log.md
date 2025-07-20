Date: 2025-07-14 

This document tracks the results of end-to-end testing of the Expandr client application communicating with the local FastAPI backend proxy. 

Test ID 

Description 

Steps 

Expected Result 

Status (Pass/Fail) 

Notes 

Happy Path 

 

 

 

 

 

E2E-01 

Successful prompt generation in Notepad 

1. In Notepad, type ::Prompt(write a short poem about python) and press Space. 

Client: Generating... text appears, then is replaced by the augmented prompt being copied to the clipboard. A success sound plays.  
Server: Logs show a POST /api/v1/generate-prompt request with a 200 OK response. 

fail 

Backspacing is erroneous. 

First backspacing pattern: backspacing stops at “::Prompt(g” so the command, bracket, plus one character, and appends “Generating” without the “...” 
 
Second backspacing pattern: backspacing stops leaving just one “:”. 

E2E-02 

Successful prompt generation in VS Code 

1. In a VS Code editor, type ::Prompt(explain python decorators) and press Space. 

Client & Server: Same as E2E-01. Verifies functionality in a different application. 

pass 

Works as intended apart from backspacing issue. 

 

The second call to API returns result much faster in <5 seconds, while first call takes ~15-20 

Edge Cases 

 

 

 

 

 

E2E-03 

Empty prompt query 

1. In Notepad, type ::Prompt() and press Space. 

Client: The command is treated as normal text, no API call is made. The buffer is cleared.  
Server: No request is received. 

pass 

 

E2E-04 

Query with special characters 

1. In a web browser text area, type ::Prompt(what is "x=5" in python?) and press Space. 

Client & Server: Same as E2E-01. System should handle standard characters without issue. 

pass 

 

Error Handling 

 

 

 

 

 

E2E-05 

Backend server is not running 

1. Stop the backend server (Ctrl+C).  
2. In Notepad, type ::Prompt(test) and press Space. 

Client: After a timeout, the inline error message [Prompt Generation Failed. Try Again] should appear. Client logs should show a network error.  
Server: N/A. 

uncertain 

 
2025-07-14 10:34:32 - httpcore.connection - [DEBUG] - _trace.trace:47 - connect_tcp.started host='127.0.0.1' port=8000 local_address=None timeout=30.0 socket_options=None 2025-07-14 10:34:32 - httpcore.connection - [DEBUG] - _trace.trace:47 - connect_tcp.complete return_value=<httpcore._backends.sync.SyncStream object at 0x000001EE5DCD8850> 2025-07-14 10:34:32 - httpcore.http11 - [DEBUG] - _trace.trace:47 - send_request_headers.started request=<Request [b'POST']> 2025-07-14 10:34:32 - httpcore.http11 - [DEBUG] - _trace.trace:47 - send_request_headers.complete 2025-07-14 10:34:32 - httpcore.http11 - [DEBUG] - _trace.trace:47 - send_request_body.started request=<Request [b'POST']> 2025-07-14 10:34:32 - httpcore.http11 - [DEBUG] - _trace.trace:47 - send_request_body.complete 2025-07-14 10:34:32 - httpcore.http11 - [DEBUG] - _trace.trace:47 - receive_response_headers.started request=<Request [b'POST']> 2025-07-14 10:34:38 - src.core.focus_tracker - [INFO] - focus_tracker._focus_tracker_loop:68 - FocusTracker: Focus changed. New window handle: 1838868 2025-07-14 10:34:38 - src.core.focus_tracker - [INFO] - focus_tracker._focus_tracker_loop:75 - FocusTracker: Buffer cleared due to focus change. 2025-07-14 10:34:38 - src.core.keystroke_listener - [DEBUG] - keystroke_listener.clear_buffer:143 - KeystrokeListener: Buffer cleared 2025-07-14 10:35:02 - httpcore.http11 - [DEBUG] - _trace.trace:47 - receive_response_headers.failed exception=ReadTimeout(TimeoutError('timed out')) 2025-07-14 10:35:02 - httpcore.http11 - [DEBUG] - _trace.trace:47 - response_closed.started 2025-07-14 10:35:02 - httpcore.http11 - [DEBUG] - _trace.trace:47 - response_closed.complete 

 
I think it’s trying to detect a command before knowing it’s a prompt, maybe the conditionals on actions based on whether or not the command should be found in storage or call the api needs work:  
2025-07-14 10:34:27 - src.core.keystroke_listener - [DEBUG] - keystroke_listener._track_keystrokes:86 - Space detected. Buffer before check: '::Prompt(write some test cases' 2025-07-14 10:34:27 - src.core.keystroke_listener - [DEBUG] - keystroke_listener._track_keystrokes:117 - Checking for command: '::Prompt(write some test cases' 

2025-07-14 10:34:27 - src.core.keystroke_listener - [DEBUG] - keystroke_listener._track_keystrokes:125 - Command '::Prompt(write some test cases' not found in storage. 2025-07-14 10:34:27 - src.core.keystroke_listener - [DEBUG] - keystroke_listener._track_keystrokes:128 - Buffer after space added: '::Prompt(write some test cases ' 

 

Known Bug Investigation 

 

 

 

 

 

E2E-06 

Long prompt query 

1. Find a long block of text (e.g., 500+ words) and copy it.  
2. In Notepad, type ::Prompt( and paste the text, then add ) and press Space. 

Observe: Does the command trigger? Does the backend 

fail 

Note: currently copy pasting doesnt work since we are using a keystrokes tracker + buffer feature to determine if the typed command is a prompt or not. 
 
Perhaps we must work on a more robust check, where we just analyze the text between the “(“ immediately after “Prompt” and the last “)” and use that as our query instead of our buffer 
 
analyzing code : if self.buffer.startswith(llm_prefix) and self.buffer.endswith(")"): 

                if len(self.buffer)> len(llm_prefix) +1: 

                    user_query = self.buffer[len(llm_prefix):-1] 

 
It seems like we are indeed analyzing the buffer instead of what’s actually being typed on the user’s screen. If it’s an easy/quick workaround or fix, we can do it otherwise put it out of scope for the mvp. 
 
test for long queries by manually typing: 
 
note how the buffer suddenly got trimmed, that is a previous feature that we developed so we should remove it if and only if it’s a ::Prompt command 
 
2025-07-14 10:43:12 - src.core.keystroke_listener - [DEBUG] - keystroke_listener._track_keystrokes:132 - Buffer after adding char 'e': '::Prompt(write me a detailed interview preparation based on the context that i will provide you in the next text input, which are my resume and cover letter. you are to help me ace an upcoming intervie' 2025-07-14 10:43:12 - src.core.keystroke_listener - [DEBUG] - keystroke_listener._track_keystrokes:137 - Buffer trimmed: 'etter. you are to help me ace an upcoming intervie' 2025-07-14 10:43:12 - src.core.keystroke_listener - [DEBUG] - keystroke_listener._track_keystrokes:52 - --- _track_keystrokes CALLED: event_type=up, name=i --- 2025-07-14 10:43:12 - src.core.keystroke_listener - [DEBUG] - keystroke_listener._track_keystrokes:52 - --- _track_keystrokes CALLED: event_type=up, name=e --- 2025-07-14 10:43:12 - src.core.keystroke_listener - [DEBUG] - keystroke_listener._track_keystrokes:52 - --- _track_keystrokes CALLED: event_type=down, name=w --- 2025-07-14 10:43:12 - src.core.keystroke_listener - [DEBUG] - keystroke_listener._track_keystrokes:64 - Keystroke detected: w 2025-07-14 10:43:12 - src.core.keystroke_listener - [DEBUG] - keystroke_listener._track_keystrokes:132 - Buffer after adding char 'w': 'etter. you are to help me ace an upcoming interview' 

 

