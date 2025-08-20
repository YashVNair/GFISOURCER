import tkinter as tk
from tkinter import ttk, messagebox
import webview
import threading
import json
import os

class Api:
    def __init__(self, parent):
        self.parent = parent

    def capture_selector(self, selector):
        # This method is called from JavaScript
        self.parent.add_selector("New Field", selector)

class VisualTaggerWindow(tk.Toplevel):
    def __init__(self, master, url, company_name):
        super().__init__(master)
        self.title(f"Controls - {company_name}")
        self.geometry("400x600")
        self.url = url
        self.company_name = company_name
        self.selectors = {}

        self.create_widgets()
        self.load_website()

    def create_widgets(self):
        ttk.Label(self, text="Tagged Elements", font=("Arial", 12, "bold")).pack(pady=10)

        # A treeview to display tagged elements
        self.selectors_tree = ttk.Treeview(self, columns=("Field", "Selector"), show="headings")
        self.selectors_tree.heading("Field", text="Field")
        self.selectors_tree.heading("Selector", text="Selector")
        self.selectors_tree.column("Field", width=100)
        self.selectors_tree.column("Selector", width=300)
        self.selectors_tree.pack(fill=tk.BOTH, expand=True, padx=10)
        self.selectors_tree.bind("<Double-1>", self._on_tree_double_click)

        # Save button
        self.save_button = ttk.Button(self, text="Save Configuration", command=self.save_configuration)
        self.save_button.pack(pady=10)

    def load_website(self):
        thread = threading.Thread(target=self._start_webview)
        thread.daemon = True
        thread.start()

    def _start_webview(self):
        self.webview_api = Api(self)
        # The webview window is separate from the tkinter window
        webview.create_window(f'Tagger - {self.company_name}', self.url, js_api=self.webview_api)
        webview.start(self._inject_js)

    def _inject_js(self):
        js_code = """
            document.addEventListener('click', function(e) {
                e.preventDefault();
                e.stopPropagation();

                function getCssSelector(el) {
                    if (!(el instanceof Element)) return;
                    var path = [];
                    while (el.nodeType === Node.ELEMENT_NODE) {
                        var selector = el.nodeName.toLowerCase();
                        if (el.id) {
                            selector += '#' + el.id;
                            path.unshift(selector);
                            break;
                        } else {
                            var sib = el, nth = 1;
                            while (sib = sib.previousElementSibling) {
                                if (sib.nodeName.toLowerCase() == selector)
                                   nth++;
                            }
                            if (nth != 1)
                                selector += ":nth-of-type("+nth+")";
                        }
                        path.unshift(selector);
                        el = el.parentNode;
                    }
                    return path.join(" > ");
                }

                var selector = getCssSelector(e.target);
                window.pywebview.api.capture_selector(selector);
            }, true);
        """
        # We need to get the active window to evaluate JS
        window = webview.active_window()
        if window:
            window.evaluate_js(js_code)

    def add_selector(self, field, selector):
        # Called from the Api class, needs to be thread-safe
        self.after(0, self._add_selector_to_tree, field, selector)

    def _add_selector_to_tree(self, field, selector):
        self.selectors_tree.insert("", "end", values=(field, selector))

    def _on_tree_double_click(self, event):
        region = self.selectors_tree.identify_region(event.x, event.y)
        if region != "cell":
            return

        column = self.selectors_tree.identify_column(event.x)
        if column != "#1": # Only allow editing the "Field" column
            return

        item = self.selectors_tree.identify_row(event.y)

        x, y, width, height = self.selectors_tree.bbox(item, column)

        entry = ttk.Entry(self.selectors_tree)
        entry.place(x=x, y=y, width=width, height=height)

        entry.insert(0, self.selectors_tree.item(item, "values")[0])
        entry.focus_force()

        entry.bind("<Return>", lambda e: self._on_entry_edit(entry, item))
        entry.bind("<FocusOut>", lambda e: self._on_entry_edit(entry, item))

    def _on_entry_edit(self, entry, item):
        new_value = entry.get()
        current_values = list(self.selectors_tree.item(item, "values"))
        current_values[0] = new_value
        self.selectors_tree.item(item, values=tuple(current_values))
        entry.destroy()

    def save_configuration(self):
        config_dir = os.path.join(os.path.dirname(__file__), "configs")
        os.makedirs(config_dir, exist_ok=True)

        config_data = {}
        for item in self.selectors_tree.get_children():
            values = self.selectors_tree.item(item, "values")
            field = values[0]
            selector = values[1]
            if field and selector and field != "New Field":
                config_data[field] = selector

        if not config_data:
            messagebox.showwarning("Warning", "No fields have been configured. Please tag some elements and name the fields.")
            return

        file_path = os.path.join(config_dir, f"{self.company_name}.json")
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(config_data, f, indent=4)

            messagebox.showinfo("Success", f"Configuration saved to {file_path}")

            # Automatically add the company to the main GUI
            if hasattr(self.master, 'add_company_from_tagger'):
                self.master.add_company_from_tagger(self.company_name, "visual", self.url)

            self.destroy()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save configuration.\n{e}")

if __name__ == '__main__':
    # This is for testing the window independently
    root = tk.Tk()
    root.title("Main Window")
    # Create a dummy main window for the Toplevel to attach to.
    # The Toplevel will be the main interaction window for this test.
    app = VisualTaggerWindow(root, "https://pywebview.flowrl.com/hello", "TestCompany")
    root.mainloop()
