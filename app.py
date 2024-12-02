from flask import Flask, render_template, request, send_file
import os
import check  # Import your check.py module
import pandas as pd  # Import pandas to read Excel files

app = Flask(__name__)

# Enable template auto-reloading
app.config['TEMPLATES_AUTO_RELOAD'] = True

@app.route('/')
def welcome():
    # Display the welcome page
    return render_template('welcome.html')

@app.route('/input', methods=['GET', 'POST'])
def input_page():
    if request.method == 'POST':
        try:
            # Collect form data
            username = request.form['user_name']
            print(f"Username received: {username}")  # Debug print to verify the username
            inputs = {
                'initial_age': int(request.form['current_age']),
                'retirement_age': int(request.form['retirement_age']),
                'monthly_expenses': float(request.form['monthly_expenses']),
                'monthly_in_hand': float(request.form['monthly_salary']),
                'initial_pf_corpus': float(request.form['pf_corpus']),
                'monthly_pf_contribution': float(request.form['pf_contribution']),
                'initial_current_corpus': float(request.form['investment_corpus']),
                'goals': []
            }

            num_goals = int(request.form['num_goals'])
            for i in range(1, num_goals + 1):
                goal = {
                    'amount': float(request.form[f'goal_{i}_target']),
                    'years': int(request.form[f'goal_{i}_years'])
                }
                inputs['goals'].append(goal)

            # Run the financial planning script with collected inputs
            result = check.main(data=inputs)

            if result['success']:
                # Generate the output file name with the user's name
                output_filename = f"financial_report_{username}.xlsx"
                output_file_path = os.path.join('static/generated_files', output_filename)

                # Ensure the file is moved to the correct static folder
                if not os.path.exists(output_file_path):
                    os.rename(result['output_path'], output_file_path)  # Move the file to static folder

                # Read the "Summary" sheet using pandas
                summary_data = pd.read_excel(output_file_path, sheet_name='Summary')

                # Convert the dataframe to HTML (you can format it as needed)
                summary_html = summary_data.to_html(classes='table table-bordered', index=False)

                # Pass username to result.html
                return render_template(
                    'result.html',
                    username=username,  # Pass the username here
                    output_path=output_filename,  # Pass the file name to the result page
                    file_path=output_file_path,  # Pass the static file path for download
                    summary_html=summary_html  # Pass the HTML table of the summary data
                )
            else:
                return f"An error occurred: {result.get('error', result.get('message'))}", 500

        except Exception as e:
            return render_template(
                'error.html',
                error_message=f"An unexpected error occurred: {str(e)}"
            ), 500
    else:
        # Render the input form page
        return render_template('input_form.html')

@app.route('/download/<filename>')
def download_file(filename):
    try:
        # Define the path to the static folder or where the file is saved
        file_path = os.path.join('static/generated_files', filename)  # Static path
        return send_file(file_path, as_attachment=True)
    except Exception as e:
        return f"Error: {str(e)}", 500

if __name__ == '__main__':
    app.run(debug=True)
