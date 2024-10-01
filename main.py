from smtplib import SMTP
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import os
from os import system  # rensa terminalen
import json
from dataclasses import dataclass
from dotenv import load_dotenv

load_dotenv()

os.chdir(os.path.dirname(__file__))

PASSWORD = os.environ.get("PASSWORD_EMAIL")
EMAIL_SENDER = os.environ.get("EMAIL_SENDER")
EMPLOYEE_DATA_PATH = r"./employees.json"


@dataclass(repr=True)
class Employee:
    name: str
    email: str
    department: str
    team: int | str = 1  # I assign the teams in numbers other might use text


class EmployeeDataManager(Employee):
    """
    This data manager uses JSON file to manage employee data

    jag använde json för delvis visa jag kan om json och API
    men tänker spara projekt för framtid kan återvända kod ksk
    Jag vet den följer inte PEP8
    """

    def __init__(self) -> None:
        self.data: dict = self.load_employee_data()  # json dict
        self.department = self.get_department()

    def add_department(self) -> None:
        new_department_name = input(
            "What is the name of the new department (name + Department)? "
        )

        new_data = {new_department_name: []}

        self.data |= new_data  # puts the new data in the self.data

        self.upload_json_data(self.data)

    def add_employee(self) -> list[Employee]:
        """Add an employee to the company"""
        departments_names: list[str] = list(self.data.keys())

        for index, department in enumerate(
            departments_names
        ):  # lista ut i terminalen vilka e departments
            print(index + 1, department)

        department_choice: str = (
            int(input("Which department to add the new employe to ")) - 1
        )

        employee_name: str = input("Enter the name of the employee")
        employee_email: str = input("Enter the email of the employee")
        employee_team: int = int(input("Enter the team of the employee"))

        new_employee = Employee(
            employee_name, employee_email, department_choice, employee_team
        )
        self.data[departments_names[department_choice]].append(new_employee.__dict__)
        self.upload_json_data(self.data)  # skickar data

    def get_all_employees(self) -> list[Employee]:
        """Return a list of all employees as Employee objects"""
        employee_list = []

        departments: list[str] = list(self.data.keys())

        for department in departments:
            employees = self.data[department]

            for employee in employees:
                employee_list.append(
                    Employee(
                        name=employee["name"],
                        email=employee["email"],
                        department=department,
                        team=employee["team"],
                    )
                )

        return employee_list

    def get_department(self) -> list[Employee]:
        """Return a list of all employees in a department"""
        employee_list: list[Employee] = []  # choices

        departments = list(self.data.keys())

        for index, department_name in enumerate(departments):
            print(f"{index + 1}. {department_name}")

        department_number = int(
            input("Choose a department: ")
        )  # select department with a number == index
        department = self.data.get(departments[department_number - 1])

        for employee in department:
            employee_list.append(
                Employee(
                    employee["name"],
                    employee["email"],
                    departments[department_number - 1],
                    employee["team"],
                )
            )

        return employee_list

    def get_department_team(self) -> list[str]:
        """Return a list of all employees that are part of a team in a department as Employee objects"""

        department_team = list(
            set(employee.team for employee in self.department)
        )  # list of employees in that department

        print("Available teams:")
        for index, person in enumerate(
            department_team, start=1
        ):  # print all the available team
            print(f"team {index}: {person}")

        team_to_send = int(input("Enter the team name: "))

        # check if employee is part of the team
        return [
            employee.email
            for employee in self.department
            if employee.team == team_to_send
        ]

    def load_employee_data(self) -> dict:
        """
        This function reads the employee data from the specified JSON file and returns it as a dictionary.
        """
        with open(EMPLOYEE_DATA_PATH, "r") as file:
            return json.load(file)

    def upload_json_data(self, data) -> None:
        """
        This function writes the provided data to the specified JSON file.
        """
        with open(EMPLOYEE_DATA_PATH, "a") as file:
            json.dump(data, file, indent=4)


class EmployeeEmailSender(EmployeeDataManager):
    def __init__(self, message: str) -> None:
        self.message = MIMEText(message, "plain")
        self.server = SMTP("smtp.gmail.com", port=587)
        self.server.starttls()  # start tls server
        self.server.login(EMAIL_SENDER, password=PASSWORD)

    def send_email(self, recipient: list[Employee]) -> None:
        """
        This function sends email to the selected employees.

        return: list objects of class Employee
        """
        msg = MIMEMultipart()
        msg["From"] = EMAIL_SENDER
        msg["To"] = ", ".join(recipient.email)
        msg["Subject"] = "Test Email"
        msg.attach(self.message)

        try:
            self.server.sendmail(EMAIL_SENDER, ", ".join(recipient.email), self.message)
            print("Email sent successfully.")
        except Exception as e:
            print(f"Error sending email: {e}")


def main():
    while True:
        print(
            "also use EmployeeDataManager to check \
                if the file management works properly"
        )

        print("\nChoose an option:")
        print("1. Add a new department")
        print("2. Add a new employee")
        print("3. Send email to all employees")
        print("4. Send email to all employees in a department")
        print("5. Send email to a specific team")
        print(
            "6. Send email test to one or more people (u need to prep code beforehand for test)"
        )
        print("0. Exit")
        choice = int(input("Enter your choice: "))
        system("cls || clear")
        match choice:
            case 1:
                EmployeeDataManager().add_department()
                break

            case 2:
                EmployeeDataManager().add_employee()
                break

            case 3:
                employees = EmployeeDataManager().get_all_employees()
                sender = EmployeeEmailSender("This is a test email.")
                sender.send_email(employees)
                print("Email sent successfully.")
                break

            case 4:
                employees = EmployeeDataManager().get_department()
                sender = EmployeeEmailSender("This is a test email.")
                sender.send_email(employees)
                print("Email sent successfully.")
                break

            case 5:
                employees = EmployeeDataManager().get_department_team()
                sender = EmployeeEmailSender("This is a test email.")
                sender.send_email(employees)
                break

            case 0:
                print("Exiting...")
                break

            case _:
                system("cls || clear")
                print("Invalid choice.")
                continue


if __name__ == "__main__":
    main()
