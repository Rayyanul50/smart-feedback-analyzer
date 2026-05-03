import tkinter as tk
from tkinter import ttk, scrolledtext, filedialog, messagebox
import pandas as pd
from ibm_watson import NaturalLanguageUnderstandingV1
from ibm_watson.natural_language_understanding_v1 import Features, SentimentOptions, KeywordsOptions
from ibm_cloud_sdk_core.authenticators import IAMAuthenticator
import json
from datetime import datetime

class FeedbackAnalyzerGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Smart Feedback Analyzer - IBM Watson")
        self.root.geometry("900x700")
        self.root.configure(bg='#f0f0f0')
        
        # Initialize IBM Watson client
        self.nlu = None
        
        # Setup GUI
        self.setup_gui()
        
        # Load API credentials if available
        self.load_credentials()
    
    def setup_gui(self):
        # Title Frame
        title_frame = tk.Frame(self.root, bg='#2c3e50', height=80)
        title_frame.pack(fill='x')
        title_frame.pack_propagate(False)
        
        title_label = tk.Label(title_frame, text="🤖 Smart Feedback Analyzer", 
                               font=('Arial', 24, 'bold'), bg='#2c3e50', fg='white')
        title_label.pack(pady=20)
        
        # Main Container
        main_container = tk.Frame(self.root, bg='#f0f0f0')
        main_container.pack(fill='both', expand=True, padx=20, pady=20)
        
        # Left Panel - Input
        left_panel = tk.Frame(main_container, bg='white', relief='raised', bd=1)
        left_panel.pack(side='left', fill='both', expand=True, padx=(0, 10))
        
        # Right Panel - Results
        right_panel = tk.Frame(main_container, bg='white', relief='raised', bd=1)
        right_panel.pack(side='right', fill='both', expand=True, padx=(10, 0))
        
        # ===== LEFT PANEL CONTENT =====
        # API Configuration Section
        api_frame = tk.LabelFrame(left_panel, text="IBM Watson Configuration", 
                                  font=('Arial', 12, 'bold'), bg='white', padx=10, pady=10)
        api_frame.pack(fill='x', padx=10, pady=10)
        
        tk.Label(api_frame, text="API Key:", bg='white').grid(row=0, column=0, sticky='w', pady=5)
        self.api_key_entry = tk.Entry(api_frame, width=40, show='*')
        self.api_key_entry.grid(row=0, column=1, pady=5, padx=5)
        
        tk.Label(api_frame, text="Service URL:", bg='white').grid(row=1, column=0, sticky='w', pady=5)
        self.url_entry = tk.Entry(api_frame, width=40)
        self.url_entry.grid(row=1, column=1, pady=5, padx=5)
        self.url_entry.insert(0, "https://api.us-south.natural-language-understanding.watson.cloud.ibm.com")
        
        # Add help text for getting credentials
        help_text = tk.Label(api_frame, text="💡 Get free API key from: cloud.ibm.com", 
                            bg='white', fg='blue', font=('Arial', 8))
        help_text.grid(row=2, column=0, columnspan=2, pady=5)
        
        self.connect_btn = tk.Button(api_frame, text="🔌 Connect to Watson", 
                                     command=self.connect_watson, bg='#3498db', fg='white',
                                     font=('Arial', 10, 'bold'))
        self.connect_btn.grid(row=3, column=0, columnspan=2, pady=10)
        
        # Input Section
        input_frame = tk.LabelFrame(left_panel, text="Feedback Input", 
                                    font=('Arial', 12, 'bold'), bg='white', padx=10, pady=10)
        input_frame.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Single feedback entry
        tk.Label(input_frame, text="Enter single feedback:", bg='white', 
                font=('Arial', 10)).pack(anchor='w')
        
        self.feedback_text = scrolledtext.ScrolledText(input_frame, height=8, width=40)
        self.feedback_text.pack(fill='x', pady=5)
        
        # Add sample button
        self.sample_btn = tk.Button(input_frame, text="📝 Load Sample Feedback", 
                                    command=self.load_sample, bg='#34495e', fg='white',
                                    font=('Arial', 9))
        self.sample_btn.pack(pady=5)
        
        self.analyze_btn = tk.Button(input_frame, text="🔍 Analyze Feedback", 
                                     command=self.analyze_single, bg='#2ecc71', fg='white',
                                     font=('Arial', 10, 'bold'), state='disabled')
        self.analyze_btn.pack(pady=10)
        
        # Batch upload option
        tk.Label(input_frame, text="- OR -", bg='white', font=('Arial', 10)).pack()
        
        self.upload_btn = tk.Button(input_frame, text="📁 Upload CSV File", 
                                    command=self.upload_csv, bg='#9b59b6', fg='white',
                                    font=('Arial', 10, 'bold'))
        self.upload_btn.pack(pady=10)
        
        self.file_label = tk.Label(input_frame, text="No file selected", bg='white', fg='gray')
        self.file_label.pack()
        
        # ===== RIGHT PANEL CONTENT =====
        # Results Section
        self.results_frame = tk.LabelFrame(right_panel, text="Analysis Results", 
                                           font=('Arial', 12, 'bold'), bg='white', padx=10, pady=10)
        self.results_frame.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Results display
        self.results_text = scrolledtext.ScrolledText(self.results_frame, height=20, width=50,
                                                       font=('Courier', 10))
        self.results_text.pack(fill='both', expand=True)
        
        # Clear results button
        clear_btn = tk.Button(self.results_frame, text="🗑️ Clear Results", 
                              command=self.clear_results, bg='#e74c3c', fg='white',
                              font=('Arial', 9))
        clear_btn.pack(pady=5)
        
        # Export button
        self.export_btn = tk.Button(right_panel, text="💾 Export Results", 
                                    command=self.export_results, bg='#e67e22', fg='white',
                                    font=('Arial', 10, 'bold'), state='disabled')
        self.export_btn.pack(pady=10)
        
        # Status bar
        self.status_bar = tk.Label(self.root, text="Ready - Connect to IBM Watson to start", 
                                   bd=1, relief='sunken', anchor='w', bg='#ecf0f1')
        self.status_bar.pack(side='bottom', fill='x')
        
        self.results_data = []
    
    def load_sample(self):
        """Load sample feedback for testing"""
        sample = "The product is amazing! Works exactly as described. Very happy with my purchase."
        self.feedback_text.delete("1.0", tk.END)
        self.feedback_text.insert("1.0", sample)
        self.status_bar.config(text="📝 Sample feedback loaded")
    
    def load_credentials(self):
        """Try to load credentials from config file"""
        try:
            from config import API_KEY, SERVICE_URL
            self.api_key_entry.insert(0, API_KEY)
            self.url_entry.delete(0, tk.END)
            self.url_entry.insert(0, SERVICE_URL)
        except:
            pass  # No config file, user will enter manually
    
    def connect_watson(self):
        """Connect to IBM Watson service"""
        api_key = self.api_key_entry.get().strip()
        service_url = self.url_entry.get().strip()
        
        if not api_key or not service_url:
            messagebox.showerror("Error", "Please enter both API Key and Service URL")
            return
        
        try:
            authenticator = IAMAuthenticator(api_key)
            self.nlu = NaturalLanguageUnderstandingV1(
                version='2021-08-01',
                authenticator=authenticator
            )
            self.nlu.set_service_url(service_url)
            
            # Test connection with a simple analysis
            test_result = self.nlu.analyze(
                text="Test connection",
                features=Features(sentiment=SentimentOptions())
            ).get_result()
            
            self.analyze_btn.config(state='normal')
            self.status_bar.config(text="✅ Connected to IBM Watson successfully!")
            messagebox.showinfo("Success", "Connected to IBM Watson successfully!")
            
        except Exception as e:
            messagebox.showerror("Connection Error", f"Failed to connect: {str(e)}")
            self.status_bar.config(text="❌ Connection failed")
    
    def analyze_single(self):
        """Analyze single feedback text"""
        if not self.nlu:
            messagebox.showerror("Error", "Please connect to Watson first")
            return
        
        feedback = self.feedback_text.get("1.0", tk.END).strip()
        if not feedback:
            messagebox.showwarning("Warning", "Please enter some feedback to analyze")
            return
        
        self.status_bar.config(text="🔄 Analyzing feedback...")
        self.root.update()
        
        try:
            response = self.nlu.analyze(
                text=feedback,
                features=Features(
                    sentiment=SentimentOptions(),
                    keywords=KeywordsOptions(limit=5)
                )
            ).get_result()
            
            # Extract sentiment
            sentiment = response['sentiment']['document']['label'].upper()
            score = response['sentiment']['document']['score']
            
            # Extract keywords
            keywords = [kw['text'] for kw in response.get('keywords', [])]
            
            # Display results
            self.display_result(feedback, sentiment, score, keywords)
            
            # Store for export
            self.results_data.append({
                'feedback': feedback,
                'sentiment': sentiment,
                'score': score,
                'keywords': ', '.join(keywords),
                'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            })
            
            self.export_btn.config(state='normal')
            self.status_bar.config(text="✅ Analysis complete!")
            
        except Exception as e:
            messagebox.showerror("Analysis Error", f"Failed to analyze: {str(e)}")
            self.status_bar.config(text="❌ Analysis failed")
            print(f"Detailed error: {str(e)}")  # For debugging
    
    def display_result(self, feedback, sentiment, score, keywords):
        """Display analysis result in the results panel"""
        # Color code based on sentiment
        if sentiment == "POSITIVE":
            sentiment_emoji = "😊"
            color_tag = "positive"
        elif sentiment == "NEGATIVE":
            sentiment_emoji = "😞"
            color_tag = "negative"
        else:
            sentiment_emoji = "😐"
            color_tag = "neutral"
        
        result = f"""
{'='*60}
📝 FEEDBACK:
{feedback[:300]}{'...' if len(feedback) > 300 else ''}

{'='*60}
🎯 ANALYSIS RESULT:
Sentiment: {sentiment_emoji} {sentiment}
Confidence Score: {score:.3f}
Top Keywords: {', '.join(keywords) if keywords else 'No keywords detected'}

📊 Interpretation: {self.get_interpretation(sentiment, score)}
{'='*60}

"""
        self.results_text.insert(tk.END, result)
        
        # Configure text tags for colors
        self.results_text.tag_config("positive", foreground="green")
        self.results_text.tag_config("negative", foreground="red")
        self.results_text.tag_config("neutral", foreground="orange")
        
        # Apply color to sentiment text
        start_idx = self.results_text.search(f"Sentiment: {sentiment_emoji} {sentiment}", 
                                             "1.0", tk.END)
        if start_idx:
            end_idx = f"{start_idx}+{len(f'Sentiment: {sentiment_emoji} {sentiment}')}c"
            self.results_text.tag_add(color_tag, start_idx, end_idx)
        
        self.results_text.see(tk.END)
    
    def get_interpretation(self, sentiment, score):
        """Get human-readable interpretation"""
        if sentiment == "POSITIVE":
            if score > 0.7:
                return "Very positive feedback! The customer is highly satisfied."
            else:
                return "Positive feedback with moderate enthusiasm."
        elif sentiment == "NEGATIVE":
            if score < -0.7:
                return "Strongly negative feedback. Urgent action recommended!"
            else:
                return "Negative feedback. Some issues need attention."
        else:
            return "Neutral feedback. Customer is neither particularly happy nor unhappy."
    
    def clear_results(self):
        """Clear the results display"""
        self.results_text.delete("1.0", tk.END)
        self.status_bar.config(text="Results cleared")
    
    def upload_csv(self):
        """Upload and analyze multiple feedbacks from CSV"""
        if not self.nlu:
            messagebox.showerror("Error", "Please connect to Watson first")
            return
        
        file_path = filedialog.askopenfilename(
            title="Select CSV File",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")]
        )
        
        if not file_path:
            return
        
        self.file_label.config(text=f"📄 {file_path.split('/')[-1]}")
        self.status_bar.config(text="🔄 Processing batch analysis...")
        self.root.update()
        
        try:
            df = pd.read_csv(file_path)
            
            # Show available columns to help user
            print(f"Available columns: {df.columns.tolist()}")
            
            # Try to find feedback column (case insensitive)
            feedback_col = None
            for col in df.columns:
                if 'feedback' in col.lower() or 'review' in col.lower() or 'comment' in col.lower():
                    feedback_col = col
                    break
            
            if feedback_col is None:
                # Use first column as feedback
                feedback_col = df.columns[0]
                response = messagebox.askyesno("Column Selection", 
                    f"Using '{feedback_col}' as feedback column. Continue?")
                if not response:
                    return
            
            feedbacks = df[feedback_col].tolist()
            
            self.results_text.delete("1.0", tk.END)
            self.results_data = []
            
            # Create progress window
            progress_window = tk.Toplevel(self.root)
            progress_window.title("Processing")
            progress_window.geometry("300x100")
            progress_label = tk.Label(progress_window, text="Analyzing feedback...")
            progress_label.pack(pady=20)
            progress_bar = ttk.Progressbar(progress_window, length=200, mode='determinate')
            progress_bar.pack(pady=10)
            
            for i, feedback in enumerate(feedbacks):
                if pd.isna(feedback) or str(feedback).strip() == '':
                    continue
                
                progress_bar['value'] = (i / len(feedbacks)) * 100
                progress_label.config(text=f"Analyzing {i+1}/{len(feedbacks)}...")
                progress_window.update()
                
                try:
                    response = self.nlu.analyze(
                        text=str(feedback),
                        features=Features(sentiment=SentimentOptions())
                    ).get_result()
                    
                    sentiment = response['sentiment']['document']['label'].upper()
                    score = response['sentiment']['document']['score']
                    
                    self.display_result(str(feedback), sentiment, score, [])
                    
                    self.results_data.append({
                        'feedback': str(feedback),
                        'sentiment': sentiment,
                        'score': score,
                        'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    })
                    
                    self.status_bar.config(text=f"🔄 Analyzed {i+1}/{len(feedbacks)}")
                    self.root.update()
                    
                except Exception as e:
                    self.results_text.insert(tk.END, f"\n❌ Error analyzing feedback #{i+1}: {str(e)}\n")
            
            progress_window.destroy()
            self.export_btn.config(state='normal')
            self.status_bar.config(text=f"✅ Batch analysis complete! Analyzed {len(self.results_data)} items")
            messagebox.showinfo("Complete", f"Successfully analyzed {len(self.results_data)} feedback entries")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to process CSV: {str(e)}")
            self.status_bar.config(text="❌ CSV processing failed")
    
    def export_results(self):
        """Export results to CSV file"""
        if not self.results_data:
            messagebox.showwarning("Warning", "No results to export")
            return
        
        file_path = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
            initialfile=f"feedback_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        )
        
        if file_path:
            df = pd.DataFrame(self.results_data)
            df.to_csv(file_path, index=False)
            messagebox.showinfo("Success", f"Results exported to {file_path}")
            self.status_bar.config(text=f"✅ Results exported to {file_path}")

def main():
    root = tk.Tk()
    app = FeedbackAnalyzerGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()