

# -----------------------Sign Up Account-----------------------------
def pstu_cse_event_account_created(username: str) -> str:
    return f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Welcome to PSTU CSE Annual Event!</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}

        body {{
            font-family: Arial, Helvetica, sans-serif;
            background-color: #f4f4f4;
            color: #333333;
            line-height: 1.6;
        }}

        .container {{
            max-width: 600px;
            width: 100%;
            margin: 0 auto;
            background-color: #ffffff;
            border-radius: 8px;
            overflow: hidden;
        }}

        .header {{
            background-color: #4CAF50;
            padding: 20px;
            text-align: center;
            color: #ffffff;
        }}

        .header h1 {{
            margin: 0;
            font-size: 24px;
            font-weight: bold;
        }}

        .content {{
            padding: 20px;
            color: #333333;
        }}

        .content h2 {{
            color: #4CAF50;
            font-size: 20px;
            margin-bottom: 15px;
        }}

        .details-table {{
            width: 100%;
            border-collapse: collapse;
            margin: 20px 0;
        }}

        .details-table th, .details-table td {{
            padding: 12px;
            border: 1px solid #dddddd;
            text-align: left;
            font-size: 14px;
        }}

        .details-table th {{
            background-color: #f9f9f9;
            font-weight: bold;
            width: 30%;
        }}

        .details-table td {{
            background-color: #ffffff;
        }}

        .button {{
            display: block;
            width: 200px;
            padding: 12px 0;
            background-color: #4CAF50;
            color: #ffffff;
            text-decoration: none;
            border-radius: 5px;
            font-weight: bold;
            margin: 20px auto 0;
            text-align: center;
        }}

        .footer {{
            text-align: center;
            padding: 20px;
            font-size: 12px;
            color: #777777;
            background-color: #f9f9f9;
            border-radius: 0 0 8px 8px;
        }}

        /* Dark mode */
        @media (prefers-color-scheme: dark) {{
            body {{
                background-color: #1a1a1a;
                color: #ffffff;
            }}
            .container {{
                background-color: #2a2a2a;
            }}
            .content {{
                color: #ffffff;
            }}
            .details-table th {{
                background-color: #333333;
                border-color: #444444;
                color: #ffffff;
            }}
            .details-table td {{
                background-color: #2a2a2a;
                border-color: #444444;
                color: #ffffff;
            }}
            .footer {{
                background-color: #222222;
                color: #aaaaaa;
            }}
        }}

        /* Mobile styles */
        @media only screen and (max-width: 600px) {{
            .container {{
                width: 100%;
                border-radius: 0;
            }}
            .header {{
                padding: 15px;
            }}
            .header h1 {{
                font-size: 20px;
            }}
            .content {{
                padding: 15px;
            }}
            .content h2 {{
                font-size: 18px;
            }}
            .details-table th,
            .details-table td {{
                padding: 8px;
                font-size: 12px;
                display: block;
                width: 100%;
                box-sizing: border-box;
            }}
            .details-table th {{
                background-color: #f0f0f0;
                border-bottom: none;
            }}
            .details-table td {{
                border-top: none;
                background-color: #ffffff;
            }}
            .button {{
                width: 90%;
                margin: 20px auto 0;
            }}
        }}
    </style>
</head>
<body>
    <center>
        <div class="container">
            <div class="header">
                <h1> CPL (CSE Premier League) </h1>
            </div>
            <div class="content">
                <h2>Hello, {username}!</h2>
                <p>Assalamualakum! We’re thrilled to have you join the <strong>Faculty of Computer Science and Engineering (CSE)</strong> at Patuakhali Science and Technology University (PSTU) for our intra faculty ckricket tounament event!</p>
                <p>Your account has been successfully created.</p>

                <p> Check out our recent Intra-University Gaming and Programming Contests.</p>
                <a href="https://pstu.ac.bd/faculty/faculty-of-computer-science-and-engineering" class="button">💥More About PSTU CSE💥</a>
            </div>
            <div class="footer">
                <p>Need help? Contact us anytime at the Faculty of CSE, PSTU.</p>
                <p>&copy;PSTU CSE. All rights reserved.</p>
            </div>
        </div>
    </center>
</body>
</html>
"""




# -----------------------Reset Account-----------------------------

def pstu_cse_reset_password(username: str, reset_link: str) -> str:
    return f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Password Reset - PSTU CSE CPL</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}

        body {{
            font-family: Arial, Helvetica, sans-serif;
            background-color: #f4f4f4;
            color: #333333;
            line-height: 1.6;
        }}

        .container {{
            max-width: 600px;
            width: 100%;
            margin: 0 auto;
            background-color: #ffffff;
            border-radius: 8px;
            overflow: hidden;
        }}

        .header {{
            background-color: #4CAF50;
            padding: 20px;
            text-align: center;
            color: #ffffff;
        }}

        .header h1 {{
            margin: 0;
            font-size: 24px;
            font-weight: bold;
        }}

        .content {{
            padding: 20px;
            color: #333333;
        }}

        .content h2 {{
            color: #4CAF50;
            font-size: 20px;
            margin-bottom: 15px;
        }}

        .button {{
            display: block;
            width: 220px;
            padding: 12px 0;
            background-color: #4CAF50;
            color: #ffffff;
            text-decoration: none;
            border-radius: 5px;
            font-weight: bold;
            margin: 20px auto 0;
            text-align: center;
        }}

        .note {{
            font-size: 13px;
            color: #777;
            margin-top: 20px;
            text-align: center;
        }}

        .footer {{
            text-align: center;
            padding: 20px;
            font-size: 12px;
            color: #777777;
            background-color: #f9f9f9;
            border-radius: 0 0 8px 8px;
        }}

        /* Dark mode */
        @media (prefers-color-scheme: dark) {{
            body {{
                background-color: #1a1a1a;
                color: #ffffff;
            }}
            .container {{
                background-color: #2a2a2a;
            }}
            .content {{
                color: #ffffff;
            }}
            .footer {{
                background-color: #222222;
                color: #aaaaaa;
            }}
        }}

        /* Mobile styles */
        @media only screen and (max-width: 600px) {{
            .container {{
                width: 100%;
                border-radius: 0;
            }}
            .header {{
                padding: 15px;
            }}
            .header h1 {{
                font-size: 20px;
            }}
            .content {{
                padding: 15px;
            }}
            .content h2 {{
                font-size: 18px;
            }}
            .button {{
                width: 90%;
                margin: 20px auto 0;
            }}
        }}
    </style>
</head>
<body>
    <center>
        <div class="container">
            <div class="header">
                <h1> CPL (CSE Premier League) </h1>
            </div>
            <div class="content">
                <h2>Hi {username},</h2>
                <p>We received a request to reset your password for your <strong>PSTU CSE CPL</strong> account.</p>
                <p>If you made this request, click the button below to set a new password:</p>
                <a href="{reset_link}" class="button">🔐 Reset Your Password</a>
                <br>
                <p>কি! passowrd মনে রাখতে পারো না 😆। আরেএ আমিও পারি না 🏏 । </p>
                <p class="note">
                    This link will expire in 10 minutes.<br>
                    If you didn’t request a password reset, please ignore this email — your account will remain secure.
                </p>
            </div>
            <div class="footer">
                <p>Need help? Contact us anytime at the Faculty of CSE, PSTU.</p>
                <p>&copy; PSTU CSE. All rights reserved.</p>
            </div>
        </div>
    </center>
</body>
</html>
"""

