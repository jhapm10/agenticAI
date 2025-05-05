import asyncio
import os
import logging
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from browser_use.agent.service import Agent
from browser_use.controller.service import Controller
from langchain_google_genai import ChatGoogleGenerativeAI
from pydantic import SecretStr, BaseModel

logging.basicConfig(level=logging.INFO)


class CheckResultStatus(BaseModel):
    launchedBrowser: str
    title: str
    titleValidation: str
    status: str
    numberOfActions: str
    NumberOfFileorTest: str
    message: str
    sucess: str


controller = Controller(output_model=CheckResultStatus)


async def site_validation():
    try:
        # Read the task from an external text file
        with open('task.txt', 'r') as file:
            task = file.read().strip()

        api_key = os.environ["GOOGLE_API_KEY"]
        os.environ["GEMINI_API_KEY"] = "AIzaSyBlORh0oPZgnsZkqVh4kZDHTRm3MI7L2WA"
        logging.info("API key loaded")
        llm = ChatGoogleGenerativeAI(model='gemini-2.0-flash', api_key=SecretStr(api_key))
        logging.info("LLM initialized")
        agent = Agent(task=task, llm=llm, controller=controller, use_vision=True)
        logging.info("Agent created")
        history = await agent.run()
        history.save_to_file('agentRun.json')
        logging.info("Agent run completed")
        test_result = history.final_result()
        validate_data = CheckResultStatus.model_validate_json(test_result)

        # Generate HTML report
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Site Validation Report</title>
        </head>
        <body>
            <h1>Site Validation Report</h1>
            <p><strong>Task:</strong> {task}</p>
            <p><strong>Launched Browser:</strong> {validate_data.launchedBrowser}</p>
            <p><strong>Title:</strong> {validate_data.title}</p>
            <p><strong>Title Validation:</strong> {validate_data.titleValidation}</p>
            <p><strong>Status:</strong> {validate_data.status}</p>
            <p><strong>Number of Files or Tests:</strong> {validate_data.NumberOfFileorTest}</p>
            <p><strong>Number of Actions:</strong> {validate_data.numberOfActions}</p>
            <p><strong>Message:</strong> {validate_data.message}</p>
            <p><strong>Success:</strong> {validate_data.sucess}</p>
        </body>
        </html>
        """

        # Write HTML to a file
        with open('result.html', 'w', encoding='utf-8') as html_file:
            html_file.write(html_content)

        print("HTML report generated: result.html")

        # Send the report via email
        #send_email('result.html')

    except Exception as e:
        logging.error(f"Error: {e}")
        print(f"Error: {e}")

#
# def send_email(file_path):
#     try:
#         # Email configuration
#         sender_email = "your_email@gmail.com"  # Replace with your email
#         sender_password = "your_email_password"  # Replace with your email password or app password
#         recipient_email = "jhaanjali107@gmail.com"
#         subject = "Site Validation Report"
#
#         # Create the email
#         message = MIMEMultipart()
#         message["From"] = sender_email
#         message["To"] = recipient_email
#         message["Subject"] = subject
#
#         # Email body
#         body = "Please find the attached site validation report."
#         message.attach(MIMEText(body, "plain"))
#
#         # Attach the HTML report
#         if os.path.exists(file_path):
#             with open(file_path, "rb") as attachment:
#                 part = MIMEBase("application", "octet-stream")
#                 part.set_payload(attachment.read())
#             encoders.encode_base64(part)
#             part.add_header(
#                 "Content-Disposition",
#                 f"attachment; filename={os.path.basename(file_path)}",
#             )
#             message.attach(part)
#             print("Attachment added and send to email.")
#         else:
#             print("Error: result.html file not found.")
#             return
#
#         # Connect to Gmail's SMTP server and send the email
#         with smtplib.SMTP("smtp.gmail.com", 587) as server:
#             server.starttls()
#             server.login("jhaanjali107@gmail.com", "Anjali@123")
#             server.sendmail("jhaanjali107@gmai.com", "jhaanjali107@gmail.com", message.as_string())
#
#         print("Email sent successfully!")
#
#     except Exception as e:
#         print(f"Error: {e}")


asyncio.run(site_validation())
# asyncio.run(send_email('result.html'))