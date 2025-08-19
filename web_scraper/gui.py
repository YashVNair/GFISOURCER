import tkinter as tk
from tkinter import ttk, messagebox
import os
import subprocess
import threading
import database
import concurrent.futures

class ScraperGUI(tk.Frame):
    def __init__(self, master=None):
        super().__init__(master)
        self.master = master
        self.master.title("Smart Protein Scraper")
        self.master.geometry("1200x700")
        self.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        self.project_dir = os.path.join(os.path.dirname(__file__), "product_scraper")
        self.companies_file_path = os.path.join(os.path.dirname(__file__), "companies.txt")

        self.create_widgets()
        self.load_companies()

    def create_widgets(self):
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill=tk.BOTH, expand=True)

        self.scraper_control_tab = ttk.Frame(self.notebook, padding=10)
        self.data_viewer_tab = ttk.Frame(self.notebook, padding=10)

        self.notebook.add(self.scraper_control_tab, text="Scraper Control")
        self.notebook.add(self.data_viewer_tab, text="Data Viewer")

        self.create_scraper_control_widgets(self.scraper_control_tab)
        self.create_data_viewer_widgets(self.data_viewer_tab)

    def create_scraper_control_widgets(self, parent_tab):
        left_frame = ttk.Frame(parent_tab)
        left_frame.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 10))
        right_frame = ttk.Frame(parent_tab)
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        ttk.Label(left_frame, text="Companies", font=("Arial", 12, "bold")).pack(anchor="w")
        list_frame = ttk.Frame(left_frame)
        list_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        self.company_listbox = tk.Listbox(list_frame, height=15, width=30)
        self.company_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.company_listbox.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.company_listbox.config(yscrollcommand=scrollbar.set)

        add_frame = ttk.Frame(left_frame)
        add_frame.pack(fill=tk.X, pady=5)
        self.new_company_entry = ttk.Entry(add_frame)
        self.new_company_entry.pack(side=tk.LEFT, expand=True, fill=tk.X)
        self.add_button = ttk.Button(add_frame, text="Add", command=self.add_company)
        self.add_button.pack(side=tk.RIGHT, padx=(5,0))
        self.remove_button = ttk.Button(left_frame, text="Remove Selected", command=self.remove_company)
        self.remove_button.pack(fill=tk.X)

        ttk.Label(right_frame, text="Scraper Log", font=("Arial", 12, "bold")).pack(anchor="w")
        log_frame = ttk.Frame(right_frame)
        log_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        self.output_text = tk.Text(log_frame, wrap=tk.WORD, state=tk.DISABLED, height=20, bg="black", fg="white")
        self.output_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        log_scrollbar = ttk.Scrollbar(log_frame, orient=tk.VERTICAL, command=self.output_text.yview)
        log_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.output_text.config(yscrollcommand=log_scrollbar.set)

        self.progress_bar = ttk.Progressbar(right_frame, orient='horizontal', mode='determinate')
        self.progress_bar.pack(fill=tk.X, pady=(5,0))

        self.run_button = ttk.Button(right_frame, text="Run All Scrapers", command=self.start_scraper_thread)
        self.run_button.pack(pady=10, fill=tk.X, ipady=5)

    def create_data_viewer_widgets(self, parent_tab):
        # ... (same as before)
        top_frame = ttk.Frame(parent_tab)
        top_frame.pack(fill=tk.X, pady=(0, 5))
        ttk.Label(top_frame, text="Scraped Products Database", font=("Arial", 12, "bold")).pack(side=tk.LEFT)
        self.refresh_button = ttk.Button(top_frame, text="Refresh Data", command=self.refresh_data_view)
        self.refresh_button.pack(side=tk.RIGHT)
        tree_frame = ttk.Frame(parent_tab)
        tree_frame.pack(fill=tk.BOTH, expand=True)
        columns = ("Brand", "Product Name", "Price (INR)", "Weight", "Availability", "Last Updated")
        self.tree = ttk.Treeview(tree_frame, columns=columns, show='headings')
        for col in columns:
            self.tree.heading(col, text=col, command=lambda _col=col: self.sort_treeview(_col, False))
            self.tree.column(col, width=150, anchor=tk.W)
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        vsb = ttk.Scrollbar(tree_frame, orient="vertical", command=self.tree.yview)
        vsb.pack(side='right', fill='y')
        self.tree.configure(yscrollcommand=vsb.set)
        hsb = ttk.Scrollbar(parent_tab, orient="horizontal", command=self.tree.xview)
        hsb.pack(side='bottom', fill='x')
        self.tree.configure(xscrollcommand=hsb.set)

    def sort_treeview(self, col, reverse):
        data = [(self.tree.set(child, col), child) for child in self.tree.get_children('')]
        data.sort(reverse=reverse)
        for index, (val, child) in enumerate(data):
            self.tree.move(child, '', index)
        self.tree.heading(col, command=lambda: self.sort_treeview(col, not reverse))

    def refresh_data_view(self):
        # ... (same as before)
        for item in self.tree.get_children():
            self.tree.delete(item)
        try:
            products = database.get_all_products()
            for product in products:
                row_values = [product.get(col, "") for col in self.tree['columns']]
                self.tree.insert("", tk.END, values=row_values)
        except Exception as e:
            messagebox.showerror("Database Error", f"Could not fetch data from the database.\n{e}")

    def load_companies(self):
        # ... (same as before)
        self.company_listbox.delete(0, tk.END)
        try:
            with open(self.companies_file_path, 'r', encoding='utf-8') as f:
                companies = [line.strip() for line in f if line.strip()]
            for company in companies:
                self.company_listbox.insert(tk.END, company)
        except FileNotFoundError:
            messagebox.showerror("Error", f"companies.txt not found at {self.companies_file_path}")

    def save_companies(self):
        # ... (same as before)
        companies = self.company_listbox.get(0, tk.END)
        with open(self.companies_file_path, 'w', encoding='utf-8') as f:
            for company in companies:
                f.write(f"{company}\n")

    def add_company(self):
        # ... (same as before)
        new_company = self.new_company_entry.get().strip()
        if new_company:
            self.company_listbox.insert(tk.END, new_company)
            self.new_company_entry.delete(0, tk.END)
            self.save_companies()
        else:
            messagebox.showwarning("Warning", "Company name cannot be empty.")

    def remove_company(self):
        # ... (same as before)
        selected_index = self.company_listbox.curselection()
        if selected_index:
            self.company_listbox.delete(selected_index)
            self.save_companies()
        else:
            messagebox.showwarning("Warning", "Please select a company to remove.")

    def start_scraper_thread(self):
        self.run_button.config(state=tk.DISABLED, text="Scraping...")
        self.output_text.config(state=tk.NORMAL)
        self.output_text.delete(1.0, tk.END)
        self.output_text.config(state=tk.DISABLED)
        thread = threading.Thread(target=self.execute_scraper, daemon=True)
        thread.start()

    def execute_scraper(self):
        try:
            # 1. Get the list of available spiders
            list_process = subprocess.run(['scrapy', 'list'], cwd=self.project_dir, capture_output=True, text=True)
            if list_process.returncode != 0:
                raise Exception(f"Failed to list spiders:\n{list_process.stderr}")

            spiders = list_process.stdout.strip().split('\n')
            if not spiders or spiders == ['']:
                raise Exception("No spiders found in the project.")

            self.master.after(0, lambda: self.progress_bar.config(maximum=len(spiders), value=0))
            self.completed_tasks = 0

            # 2. Run each spider in a thread pool
            with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
                future_to_spider = {executor.submit(self.run_spider, spider): spider for spider in spiders}
                for future in concurrent.futures.as_completed(future_to_spider):
                    spider_name = future_to_spider[future]
                    try:
                        future.result() #
                    except Exception as exc:
                        self.append_to_output(f"Spider {spider_name} generated an exception: {exc}\n")
                    finally:
                        self.completed_tasks += 1
                        self.master.after(0, lambda: self.progress_bar.config(value=self.completed_tasks))

        except Exception as e:
            self.master.after(0, self.append_to_output, f"\n--- An error occurred ---\n{e}\n")
        finally:
            self.master.after(0, self.finalize_scraper_run)

    def run_spider(self, spider_name):
        self.append_to_output(f"--- Starting spider: {spider_name} ---\n")
        process = subprocess.Popen(
            ['scrapy', 'crawl', spider_name],
            cwd=self.project_dir,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            encoding='utf-8'
        )
        for line in iter(process.stdout.readline, ''):
            self.master.after(0, self.append_to_output, line)
        process.wait()
        self.append_to_output(f"--- Finished spider: {spider_name} ---\n\n")

    def append_to_output(self, text):
        self.output_text.config(state=tk.NORMAL)
        self.output_text.insert(tk.END, text)
        self.output_text.see(tk.END)
        self.output_text.config(state=tk.DISABLED)

    def finalize_scraper_run(self):
        self.run_button.config(state=tk.NORMAL, text="Run All Scrapers")
        messagebox.showinfo("Success", "All spiders have completed their runs!")
        self.progress_bar['value'] = self.progress_bar['maximum']

if __name__ == "__main__":
    root = tk.Tk()
    app = ScraperGUI(master=root)
    app.mainloop()
