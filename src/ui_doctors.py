import tkinter as tk
from tkinter import messagebox, ttk
from tkinter.scrolledtext import ScrolledText
from db.doctor_repo import DoctorRepository


class DoctorUI:
    def __init__(self, parent):
        self.parent = parent
        self.window = tk.Toplevel(parent)
        self.window.title("Cadastro de Médicos")
        self.window.geometry("500x400")
        self.repo = DoctorRepository()

        # Form fields
        tk.Label(self.window, text="Nome:").pack(pady=(10, 0))
        self.name_entry = tk.Entry(self.window, width=40)
        self.name_entry.pack()

        tk.Label(self.window, text="CPF:").pack()
        self.cpf_entry = tk.Entry(self.window, width=40)
        self.cpf_entry.pack()

        tk.Label(self.window, text="CRM (Opcional):").pack()
        self.crm_entry = tk.Entry(self.window, width=40)
        self.crm_entry.pack()

        tk.Button(self.window, text="Salvar", command=self.create_doctor).pack(pady=8)

        # List display
        self.tree = ttk.Treeview(self.window, columns=("id", "name", "cpf", "crm"), show="headings", height=8)
        self.tree.heading("id", text="ID")
        self.tree.heading("name", text="Nome")
        self.tree.heading("cpf", text="CPF")
        self.tree.heading("crm", text="CRM")
        self.tree.column("id", width=40)
        self.tree.column("name", width=160)
        self.tree.column("cpf", width=120)
        self.tree.column("crm", width=80)
        self.tree.pack(padx=10, pady=10, fill="x")

        # CRUD actions
        action_frame = tk.Frame(self.window)
        action_frame.pack()

        tk.Button(action_frame, text="Editar Selecionado", command=self.update_doctor).pack(side="left", padx=4)
        tk.Button(action_frame, text="Excluir Selecionado", command=self.delete_doctor).pack(side="left", padx=4)

        self.refresh_list()

        self.window.protocol("WM_DELETE_WINDOW", self.close)

    def create_doctor(self):
        name = self.name_entry.get().strip()
        cpf = self.cpf_entry.get().strip()
        crm = self.crm_entry.get().strip() or None

        if not name or not cpf:
            messagebox.showerror("Erro", "Nome e CPF são obrigatórios!")
            return

        try:
            self.repo.create(name, cpf, crm)
            self.refresh_list()
            self.parent.event_generate("<<DOCTOR_UPDATED>>")
        except Exception as e:
            messagebox.showerror("Erro", str(e))

    def update_doctor(self):
        selected = self.tree.selection()
        if not selected:
            return messagebox.showwarning("Atenção", "Selecione um médico!")

        vals = self.tree.item(selected)["values"]
        doctor_id = vals[0]

        updates = {
            "name": self.name_entry.get().strip() or vals[1],
            "cpf": self.cpf_entry.get().strip() or vals[2],
            "crm": self.crm_entry.get().strip() or vals[3],
        }

        self.repo.update(doctor_id, updates)
        self.refresh_list()
        self.parent.event_generate("<<DOCTOR_UPDATED>>")

    def delete_doctor(self):
        selected = self.tree.selection()
        if not selected:
            return

        vals = self.tree.item(selected)["values"]
        doctor_id = vals[0]

        if messagebox.askyesno("Confirmar", f"Excluir médico {vals[1]}?"):
            self.repo.delete(doctor_id)
            self.refresh_list()
            self.parent.event_generate("<<DOCTOR_UPDATED>>")

    def refresh_list(self):
        self.tree.delete(*self.tree.get_children())
        for d in self.repo.list():
            self.tree.insert("", "end", values=(d["id"], d["name"], d["cpf"], d.get("crm") or ""))

    def close(self):
        self.repo.session.close()
        self.window.destroy()
