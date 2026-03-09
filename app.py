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
        self.current_focus_noun = ""

        self.title("English Article Helper")
        self.geometry("600x600") # Increased height for more text
        self.grid_columnconfigure(0, weight=1)

        self.title_label = ctk.CTkLabel(self, text="English Article Helper", font=ctk.CTkFont(size=24, weight="bold"))
        self.title_label.grid(row=0, column=0, padx=20, pady=(20, 10))

        self.input_frame = ctk.CTkFrame(self)
        self.input_frame.grid(row=1, column=0, padx=20, pady=10, sticky="ew")
        self.input_frame.grid_columnconfigure(0, weight=1)

        self.entry_label = ctk.CTkLabel(self.input_frame, text="Enter a noun, phrase, or full sentence:")
        self.entry_label.grid(row=0, column=0, padx=10, pady=(10, 5), sticky="w")
        
        self.noun_entry = ctk.CTkEntry(self.input_frame, placeholder_text="e.g., I bought book yesterday / USA / breakfast")
        self.noun_entry.grid(row=1, column=0, padx=10, pady=(0, 10), sticky="ew")

        self.check_button = ctk.CTkButton(self.input_frame, text="Analyze Phrase", command=self.start_check)
        self.check_button.grid(row=1, column=1, padx=10, pady=(0, 10))
        
        self.display_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.display_frame.grid(row=2, column=0, padx=20, pady=20, sticky="nsew")
        self.grid_rowconfigure(2, weight=1)
        self.display_frame.grid_columnconfigure(0, weight=1)
        
        self.question_label = ctk.CTkLabel(self.display_frame, text="Welcome! Enter text above to get started.", 
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
        self.current_focus_noun = ""
        user_input = self.noun_entry.get().strip()
        if not user_input:
            messagebox.showwarning("Input Required", "Please enter a noun or phrase to check.")
            return

        analysis = self.logic.analyze_input(user_input)
        self.current_focus_noun = analysis.get("focus_noun", "")
        lookup_result = analysis.get("result")

        if analysis.get("mode") == "lookup" and lookup_result:
            self.display_final_result(lookup_result, self.current_focus_noun)
            return

        start_node = self.logic.get_current_node()
        self.update_question_and_options(start_node)

    def _build_example_sentence(self, article_value, focus_noun):
        if not focus_noun:
            return ""

        noun_text = focus_noun.strip()
        if not noun_text:
            return ""

        article_normalized = str(article_value or "").lower()
        if article_normalized == "the":
            return f"Example: Please pass the {noun_text}."
        if article_normalized == "a / an":
            article_choice = "an" if noun_text[0].lower() in "aeiou" else "a"
            return f"Example: I saw {article_choice} {noun_text} near my house."
        if article_normalized.startswith("no article"):
            return f"Example: I use {noun_text} every day."
        return ""

    def update_question_and_options(self, node_data):
        for widget in self.options_frame.winfo_children():
            widget.destroy()
        
        self.question_label.configure(text=node_data["question"])
        
        # UPDATE: Display details if they exist, otherwise display empty text
        details_text = node_data.get("details", "")
        if self.current_focus_noun:
            details_text = f"Detected focus word: '{self.current_focus_noun}'.\n{details_text}".strip()
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

    def display_final_result(self, result_data, focus_noun=""):
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
        example_line = self._build_example_sentence(article_value, focus_noun)
        rule_reference = result_data.get("rule_ref")
        reference_text = f"\n\n(Reference: {rule_reference})" if rule_reference else ""
        focus_text = f"Focus noun: {focus_noun}\n\n" if focus_noun else ""
        example_text = f"\n\n{example_line}" if example_line else ""
        result_body = f"{focus_text}{body_prefix}{explanation_text}{example_text}{reference_text}"

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
        self.current_focus_noun = ""
        self.noun_entry.delete(0, 'end')
        self.question_label.configure(text="Welcome! Enter text above to get started.")
        
        # UPDATE: Clear the details label on reset
        self.details_label.configure(text="")
        
        for widget in self.options_frame.winfo_children():
            widget.destroy()


if __name__ == "__main__":
    app = ArticleApp()
    app.mainloop()
