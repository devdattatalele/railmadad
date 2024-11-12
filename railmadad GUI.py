import tkinter as tk
from tkinter import ttk, scrolledtext
import google.generativeai as genai
from datetime import datetime
import threading
import os


class RailwayHelpChatApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Railway Help Service Chat")
        self.root.geometry("800x600")

        # Configure Google AI
        genai.configure(api_key="AIzaSyDZu58-0bm3awZJXadDSEl6Uacp3-m7xDQ")

        # Initialize AI model with specific configuration
        self.generation_config = {
            "temperature": 1,
            "top_p": 0.95,
            "top_k": 64,
            "max_output_tokens": 8192,
            "response_mime_type": "text/plain",
        }

        self.model = genai.GenerativeModel(
#            model_name="gemini-1.5-flash",
            model_name="tunedModels/test1-railway-8fxpkk2gg8la",
            generation_config=self.generation_config
        )

        # Initialize chat with system instruction
        self.system_instruction = """You are a railways help service chat bot. You will only reply to railway related concern, if you are not related to railway then tell then to ask if any railway problem."""

        self.chat_session = self.model.start_chat(
            history=[]
        )

        self.setup_gui()

    def setup_gui(self):
        # Create main frame with railway-themed colors
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)

        # Title label
        title_label = ttk.Label(
            main_frame,
            text="Railway Help Service",
            font=("Arial", 16, "bold")
        )
        title_label.grid(row=0, column=0, columnspan=2, pady=(0, 10))

        # Chat display area
        self.chat_display = scrolledtext.ScrolledText(
            main_frame,
            wrap=tk.WORD,
            width=70,
            height=25,
            font=("Arial", 10)
        )
        self.chat_display.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S))
        self.chat_display.config(state=tk.DISABLED)

        # Input frame
        input_frame = ttk.Frame(main_frame)
        input_frame.grid(row=2, column=0, columnspan=2, pady=(5, 0), sticky=(tk.W, tk.E))

        # PNR Entry
        pnr_frame = ttk.Frame(input_frame)
        pnr_frame.pack(fill=tk.X, pady=(5, 5))

        pnr_label = ttk.Label(pnr_frame, text="PNR Number:")
        pnr_label.pack(side=tk.LEFT, padx=(0, 5))

        self.pnr_entry = ttk.Entry(pnr_frame, width=20)
        self.pnr_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)

        # Message input
        self.input_field = ttk.Entry(
            input_frame,
            font=("Arial", 10)
        )
        self.input_field.pack(fill=tk.X, pady=(5, 5))
        self.input_field.bind("<Return>", lambda e: self.send_message())

        # Send button
        send_button = ttk.Button(
            input_frame,
            text="Send",
            command=self.send_message
        )
        send_button.pack(pady=(0, 5))

        # Status label
        self.status_label = ttk.Label(
            main_frame,
            text="Ready",
            font=("Arial", 9)
        )
        self.status_label.grid(row=3, column=0, columnspan=2, pady=(5, 0), sticky=(tk.W))

        # Configure grid weights
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(1, weight=1)

        # Add initial message
        self.append_message("Welcome to Railway Help Service! Please enter your PNR number and describe your concern.",
                            "System")

    def append_message(self, message, sender):
        self.chat_display.config(state=tk.NORMAL)
        timestamp = datetime.now().strftime("%H:%M")

        if sender == "System":
            tag = "system"
            self.chat_display.tag_configure("system", foreground="green")
        elif sender == "You":
            tag = "user"
            self.chat_display.tag_configure("user", foreground="blue")
        else:
            tag = "assistant"
            self.chat_display.tag_configure("assistant", foreground="purple")

        self.chat_display.insert(tk.END, f"\n[{timestamp}] {sender}: ", tag)
        self.chat_display.insert(tk.END, f"{message}\n")
        self.chat_display.see(tk.END)
        self.chat_display.config(state=tk.DISABLED)

    def send_message(self):
        pnr = self.pnr_entry.get().strip()
        message = self.input_field.get().strip()

        if not message:
            return

        # Combine PNR and message if PNR is provided
        full_message = f"PNR number {pnr}. " + message if pnr else message

        self.input_field.delete(0, tk.END)
        self.append_message(full_message, "You")
        self.status_label.config(text="Processing...")
        self.input_field.config(state=tk.DISABLED)

        # Use threading to prevent GUI freezing
        threading.Thread(target=self.process_message, args=(full_message,), daemon=True).start()

    def process_message(self, message):
        try:
            response = self.chat_session.send_message(message)

            # Update GUI in the main thread
            self.root.after(0, self.handle_response, response.text)

        except Exception as e:
            self.root.after(0, self.handle_error, str(e))

    def handle_response(self, response_text):
        self.append_message(response_text, "Assistant")
        self.status_label.config(text="Ready")
        self.input_field.config(state=tk.NORMAL)

    def handle_error(self, error_message):
        self.status_label.config(text=f"Error: {error_message}")
        self.input_field.config(state=tk.NORMAL)


def main():
    root = tk.Tk()
    app = RailwayHelpChatApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()