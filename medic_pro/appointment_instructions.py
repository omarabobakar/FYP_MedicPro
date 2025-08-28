
SHOW_DOCTORS_TABLE_TO_USER = (
    "Here is the data of doctors for the selected disease. Please show the following details to the user by creating table in html language and use a heading line before table: Here is the doctors list for disease_name <br> Note: All doctors are available betwwen 7:00 Am to 9:00 Pm <br> (don't say anything else i will directly show this response to user.\n create html table and sort doctors by fee (show less fee doctors first))"
    "- Name\n"
    "- Available days\n"
    "- Clinic address\n"
    "- Fee\n"
    "- Profile\n ( must use class 'text-center' in it's 'td' tag. then inside use a tag with target='_blank' and add profile url here and use icon classes 'fa-solid fa-arrow-up-right-from-square' to show icon in i tag inside a tag)"
    
    "after creating table must ensure that you have added all of required data in both table heading and table body.\n"
    "if user ask about spesific dr. available days then must create html table and show the days in html table:"
    "-# (show days number here in sequence (1,2,3))"
    "-Day (show day name here)"
    "if user ask about his/her spesific appointment like pending appointments or something else then use provided information and respond him with that spesifics appointments"
)

SHOW_APPOINTMENTS_TABLES_TO_USER = (
    "Here is the data of user appointments. Please show the following details to the user by creating html table and use a heading line before table: Here is your appointments (say this in your own tone ) : (don't say anything else i will directly show this response to user.\n"
    "ID\n"
    "Dr. Name\n"
    "Day \n"
    "Time (must show time in 12 hours format, like: 14:00:00 change it to 2:00 pm)\n"
    "Status\n"
    "these all fields or mendatory in table so after creating table must ensure that you have added all of required data in both table heading and table body. must include appointment day and time in table body"
    " once you showed the appointment table to user. if user ask to show details about spesific appointment show him in simple para include dr. name, day, time, and status in this info"
)

FIX_APOINTMENT_DETAILS = (
    "If the user wants to fix an appointment with a selected doctor, follow these steps:\n"
    "1. Ensure the user has selected the correct doctor from the available list.\n if he selected any other doctor that is not in list you showed. then ask him to select doctor from provided list and show him names of doctors only"
    "2. Confirm the available day and time for the appointment. and ensure that selected day is available in doctor available days. if not then ask him to select available day and must ensure the selected is if from the selected doctor's available days.\n\n"
    "If any of this information is missing, prompt the user to provide the necessary details. Once all information is provided, respond with the following format:\n"
    "3. must check user entered time if it is in 12 hours format H:M then must convert it to 24 hours time formate H:M:S.\n and must ask user to enter time between 7:00 Am to 9:00 Pm"
    "- 'check_appointment_details'<br>"
    "- 'selected_doctor: doctor_name'<br>"
    "- 'available_day: day'<br>"
    "- 'appointment_time: time'<br>"
    "Note: if any neccessary info is missing then don't replay with these details. just ask him to provide missing details.\n don't ask user explicitly to provide time in 12 hours. if time is missing just ask him to enter time between 7:00 Am to 9:00 Pm "
)