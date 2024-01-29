from django.core.mail import EmailMessage
from django.conf import settings
from xhtml2pdf import pisa
from io import BytesIO
import os
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail, Attachment, FileContent, FileName, FileType, Disposition
from decouple import config
 
import base64
CSS_STYLES = """
    body {
        font-family: "Inter", Arial, sans-serif;
        background-color: rgba(204, 209, 230, 1);
        margin: 0;
        padding: 0;
        display: flex;
        justify-content: center;
        align-items: center;
        min-height: 100vh;
    }
 
    .patient {
    text-align: center;
    }
 
    .wrapper {
        display: flex;
        justify-content: center;
        align-items: center;
        flex-direction: column;
    }
 
    .logo-container {
        margin-bottom: 20px;
        position: absolute;
        top: 12px;
        left: 20px;
    }
 
    .content-container {
        background-color: #ffffff; /* White background for the container */
        border: 20px solid rgba(204, 209, 230, 1);
 
        border-radius: 5px;
        padding: 20px;
 
        text-align: center;
        max-width: 600px; /* Set a max width for the container to prevent it from getting too wide */
        margin: 10px auto; /* Center align the container */
    }
 
    .report-title {
        font-size: 24px;
        font-weight: bold;
        color: #2d3ed4; /* Blue color for the title */
        margin-bottom: 20px;
    }
 
    .patient-details-table {
        width: 90%;
        max-width: 500px;
        margin: 0 auto; /* Center align the table */
        border-collapse: collapse;
        margin-bottom: 20px;
    }
 
    .patient-details-table th,
    .patient-details-table td {
        border: 1px solid #ccc;
        padding: 8px;
    }
 
    .patient-prescription-table {
        width: 90%;
        max-width: 500px;
        margin: 0 auto; /* Center align the table */
        border-collapse: collapse;
        margin-bottom: 20px;
    }
 
    .patient-prescription-table th,
    .patient-prescription-table td {
        border: 1px solid #ccc;
        padding: 8px;
    }
    """
 
"""
Define functions for generating HTML content
"""
def generate_patient_details_html(user_obj, shape):
    return f"""
        <div>
            <p>
                <h3 class="patient">Patient's Details</h3>
            </p>
        </div>
        <table class="patient-details-table">
            <tr>
                <th>User Name</th>
                <th>Age</th>
                <th>Face Shape</th>
            </tr>
            <tr>
                <td>{user_obj.full_name}</td>
                <td>{user_obj.age}</td>
                <td>{shape}</td>
            </tr>
        </table>
    """
 
"""
Generating Eye Data in HTML content
"""
def generate_eye_data_html(data, user_obj):
    first_eye_data = data[0]
    second_eye_data = data[1]
    sph_first = 0
    sph_second = 0
   
    eye_html = ""
    eye_html += """
        <table class="patient-prescription-table">
            <tr>
                <th>EYE</th>
                <th>SPH</th>
                <th>CYL</th>
                <th>AXIS</th>
    """
   
    # Conditionally add "ADD" column based on user's age
    if int(user_obj.age) > 40:
        eye_html += "<th>ADD</th>"
 
    eye_html += """
            </tr>
        """
    
      # ---------------------------   Data for first eye  ------------------>>>
 
    if first_eye_data.test == "myopia":
        sph_first = first_eye_data.myopia_sph_power
    elif first_eye_data.test == "hyperopia":
        sph_first = first_eye_data.hyperopia_sph_power
 
    # --------------------------    Data for second eye --------------->>>
 
    if second_eye_data.test == "myopia":
        sph_second = second_eye_data.myopia_sph_power
    elif second_eye_data.test == "hyperopia":
        sph_second = second_eye_data.hyperopia_sph_power
    
    eye_html += f"""
        <tr>
            <td>{first_eye_data.eye_status.upper()}</td>
            <td>{sph_first}</td>
            <td>{first_eye_data.cyl_power}</td>
            <td>{first_eye_data.degree}</td>
    """
   
    # Conditionally add "ADD" column based on user's age
    if int(user_obj.age) > 40:
        eye_html += f"<td>{first_eye_data.age_power}</td>"
 
    eye_html += f"""
        </tr>
        <tr>
            <td>{second_eye_data.eye_status.upper()}</td>
            <td>{sph_second}</td>
            <td>{second_eye_data.cyl_power}</td>
            <td>{second_eye_data.degree}</td>
    """
 
    # Conditionally add "ADD" column based on user's age
    if int(user_obj.age) > 40:
        eye_html += f"<td>{second_eye_data.age_power}</td>"
   
    eye_html += """
        </tr>
       
        <!-- Add Disclaimer Section -->
        <tr>
            <td colspan="5">
                <div class="health-tip">
                    <p><strong>1.</strong> Blink rate of your eye is below the normal threshold of fresh eyes. Kindly reduce digital screen
                    <h3>Disclaimer:</h3>
                    <p><strong>1.</strong> The results displayed are for reference purposes only.</p>
                    <p><strong>2.</strong> If you feel the power displayed is different than your old power, then please speak with your eye doctor or call EyeMyEye and speak with the optometrist.</p>
                    <p><strong>3.</strong> Without confirmation from your eye doctor or EyeMyEye optometrist, do not use this power to make glasses.</p>
    time and relax your eyes.</p>
                </div>
            </td>
        </tr>
        <!-- Add Powered by Zukti Section -->
        <tr>
            <td colspan="5" style="text-align: center;">
                <h1>Powered by Zukti</h1>
            </td>
        </tr>
    """  
 
 
    eye_html += """
        </tr>
    """
   
    return eye_html
 
 
 
 
"""
Genrate Pdf
"""
def generate_pdf_report(user_obj, data, shape):
    patient_details_html = generate_patient_details_html(user_obj, shape)
    eye_html = generate_eye_data_html(data, user_obj)
 
    # Your HTML template
    html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <script src="https://cdnjs.cloudflare.com/ajax/libs/html2pdf.js/0.10.1/html2pdf.bundle.min.js"></script>
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <link rel="icon" href="" type="image/x-icon">
            <title>Patient's Report</title>
            <style>
                {CSS_STYLES}
            </style>
        </head>
        <body>
            <div class="wrapper">
                <!-- Your logo and content here -->
                {patient_details_html}
                {eye_html}
            </div>
           
            <script>
                // JavaScript to generate PDF
                function generatePDF() {{
                    const content = document.documentElement;
 
                    html2pdf()
                        .from(content)
                        .outputPdf()
                        .then(function (pdf) {{
                            pdf.save('report.pdf');
                        }});
                }}
 
                // Add a click event listener to the "Download Report" button
                document.getElementById('downloadBtn').addEventListener('click', generatePDF);
            </script>
        </body>
        </html>
    """
 
    # Generate the PDF
    pdf_buffer = BytesIO()
    pdf = pisa.CreatePDF(BytesIO(html_content.encode('UTF-8')), pdf_buffer)
    pdf_buffer.seek(0)
    return pdf_buffer
 
# """
# Send Email To User
# """
# def send_email_with_pdf(user_obj, data, shape):
#     try:
#         pdf_buffer = generate_pdf_report(user_obj, data, shape)
#         email = EmailMessage(
#             'Patient Report',
#             'Please find the patient report attached.',
#             settings.EMAIL_HOST_USER,
#             [user_obj.email],
#         )
#         email.attach('report.pdf', pdf_buffer.read(), 'application/pdf')
#         email.send()
#         return True
#     except Exception as e:
#         return e
 
 
def send_email_with_pdf(user_obj, data, shape):
    SEND_GRID_API_KEY = config('SEND_GRID_API_KEY')
    SEND_GRID_EMAIL = config('SEND_GRID_EMAIL')
    try:
        pdf_buffer = generate_pdf_report(user_obj, data, shape)
       
        message = Mail(
            from_email=SEND_GRID_EMAIL,
            to_emails=user_obj.email,
            subject='Patient Report',
            html_content='Please find the patient report attached.'
        )
    
        attached_file = Attachment(
            FileContent(base64.b64encode(pdf_buffer.read()).decode()),
            FileName('report.pdf'),
            FileType('application/pdf'),
            Disposition('attachment')
        )
 
        message.attachment = attached_file
 
        sg = SendGridAPIClient(SEND_GRID_API_KEY)
        response = sg.send(message)
 
        if response.status_code == 202:
            return True
    except Exception as e:
        return False