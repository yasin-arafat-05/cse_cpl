

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
                <h1>Welcome to PSTU CSE Annual Gaming Event 🎮</h1>
            </div>
            <div class="content">
                <h2>Hello, {username}!</h2>
                <p>We’re thrilled to have you join the <strong>Faculty of Computer Science and Engineering (CSE)</strong> at Patuakhali Science and Technology University (PSTU) for our annual gaming event — your platform for exciting competitions, skill-building, and fun!</p>
                <p>Your account has been successfully created. You can now register for events, participate in intra-university gaming challenges, programming contests, and connect with fellow students.</p>
                
                <table class="details-table">
                    <tr>
                        <th>Username</th>
                        <td>{username}</td>
                    </tr>
                    <tr>
                        <th>Account Status</th>
                        <td>Active</td>
                    </tr>
                    <tr>
                        <th>Faculty Founded</th>
                        <td>2003</td>
                    </tr>
                    <tr>
                        <th>Departments</th>
                        <td>5 (CSIT, CCE, EEE, Math, PME)</td>
                    </tr>
                    <tr>
                        <th>Current Students</th>
                        <td>230+</td>
                    </tr>
                    <tr>
                        <th>Graduates</th>
                        <td>400+ from 11 batches</td>
                    </tr>
                </table>

                <p>Start exploring and registering for the upcoming events today! Check out our recent Intra-University Gaming and Programming Contests.</p>
                <a href="https://cse.pstu.ac.bd/" class="button">Go to Dashboard</a>
            </div>
            <div class="footer">
                <p>Need help? Contact us anytime at the Faculty of CSE, PSTU.</p>
                <p>&copy; 2025 PSTU CSE. All rights reserved.</p>
            </div>
        </div>
    </center>
</body>
</html>
"""

