# app.py (Version 4 - With Details)

from tkinter import messagebox

import customtkinter as ctk

from logic import ArticleLogic
from rules import GUIDANCE_NODE_TYPE

ctk.set_appearance_mode("System")
ctk.set_default_color_theme("blue")

class ArticleApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.logic = ArticleLogic()

        self.title("English Article Helper")
        self.geometry("600x600") # Increased height for more text
        self.grid_columnconfigure(0, weight=1)

        self.title_label = ctk.CTkLabel(self, text="English Article Helper", font=ctk.CTkFont(size=24, weight="bold"))
        self.title_label.grid(row=0, column=0, padx=20, pady=(20, 10))

        self.input_frame = ctk.CTkFrame(self)
        self.input_frame.grid(row=1, column=0, padx=20, pady=10, sticky="ew")
        self.input_frame.grid_columnconfigure(0, weight=1)

        self.entry_label = ctk.CTkLabel(self.input_frame, text="Enter a noun or phrase:")
        self.entry_label.grid(row=0, column=0, padx=10, pady=(10, 5), sticky="w")
        
        self.noun_entry = ctk.CTkEntry(self.input_frame, placeholder_text="e.g., car, USA, breakfast...")
        self.noun_entry.grid(row=1, column=0, padx=10, pady=(0, 10), sticky="ew")

        self.check_button = ctk.CTkButton(self.input_frame, text="Check Article", command=self.start_check)
        self.check_button.grid(row=1, column=1, padx=10, pady=(0, 10))
        
        self.display_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.display_frame.grid(row=2, column=0, padx=20, pady=20, sticky="nsew")
        self.grid_rowconfigure(2, weight=1)
        self.display_frame.grid_columnconfigure(0, weight=1)
        
        self.question_label = ctk.CTkLabel(self.display_frame, text="Welcome! Enter a noun above to get started.", 
                                           font=ctk.CTkFont(size=18, weight="bold"), wraplength=550, justify="center")
        self.question_label.grid(row=0, column=0, padx=10, pady=10)

        # NEW: A dedicated label for details and examples
        self.details_label = ctk.CTkLabel(self.display_frame, text="", 
                                          font=ctk.CTkFont(size=14, slant="italic"), wraplength=550, justify="center")
        self.details_label.grid(row=1, column=0, padx=10, pady=(0, 15))

        self.options_frame = ctk.CTkFrame(self.display_frame, fg_color="transparent")
        self.options_frame.grid(row=2, column=0, pady=10, sticky="ew")
        self.options_frame.grid_columnconfigure(0, weight=1)

    def start_check(self):
        self.logic.reset()
        user_input = self.noun_entry.get().strip()
        if not user_input:
            messagebox.showwarning("Input Required", "Please enter a noun or phrase to check.")
            return
        
        lookup_result = self.logic.check_lookup_table(user_input)
        
        if lookup_result:
            self.display_final_result(lookup_result)
        else:
            start_node = self.logic.get_current_node()
            self.update_question_and_options(start_node)

    def update_question_and_options(self, node_data):
        for widget in self.options_frame.winfo_children():
            widget.destroy()
        
        self.question_label.configure(text=node_data["question"])
        
        # UPDATE: Display details if they exist, otherwise display empty text
        details_text = node_data.get("details", "")
        self.details_label.configure(text=details_text)
        
        for option_text in node_data["options"]:
            button = ctk.CTkButton(self.options_frame, text=option_text,
                                   command=lambda opt=option_text: self.handle_option_click(opt))
            button.grid(sticky="ew", padx=20, pady=5)
    
    def handle_option_click(self, selected_option):
        next_node = self.logic.process_answer(selected_option)
        
        if "question" in next_node:
            self.update_question_and_options(next_node)
        else:
            self.display_final_result(next_node)

    def display_final_result(self, result_data):
        for widget in self.options_frame.winfo_children():
            widget.destroy()

        article_value = result_data.get("article")
        is_guidance = result_data.get("type") == GUIDANCE_NODE_TYPE or article_value is None

        if is_guidance:
            result_title = "Guidance Provided (no article recommendation)"
            body_prefix = "Guidance:\n"
        else:
            article_display = str(article_value).upper()
            result_title = f"Recommended Article: '{article_display}'"
            body_prefix = ""

        explanation_text = result_data.get("explanation", "")
        rule_reference = result_data.get("rule_ref")
        reference_text = f"\n\n(Reference: {rule_reference})" if rule_reference else ""
        result_body = f"{body_prefix}{explanation_text}{reference_text}"

        self.question_label.configure(text=result_title)

        # UPDATE: Clear the details label when showing the result
        self.details_label.configure(text="")

        explanation_label = ctk.CTkLabel(
            self.options_frame,
            text=result_body,
            wraplength=500,
            justify="left",
        )
        explanation_label.grid(sticky="ew", padx=20, pady=10)

        start_over_button = ctk.CTkButton(self.options_frame, text="Start Over", command=self.reset_app)
        start_over_button.grid(pady=20)
    
    def reset_app(self):
        self.logic.reset()
        self.noun_entry.delete(0, 'end')
        self.question_label.configure(text="Welcome! Enter a noun above to get started.")
        
        # UPDATE: Clear the details label on reset
        self.details_label.configure(text="")
        
        for widget in self.options_frame.winfo_children():
            widget.destroy()


if __name__ == "__main__":
    app = ArticleApp()
    app.mainloop()