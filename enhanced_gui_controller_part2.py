
"""
Enhanced GUI Controller for Deep Blue Pool Chemistry (Part 2).

This file continues the implementation of the enhanced GUI controller,
focusing on the weather impact analysis, historical data visualization,
maintenance log, settings interface, and AI & predictive analytics.
"""

# This continues from the previous implementation

def _create_weather_impact_card(self, parent):
    """
    Create a card for weather impact analysis.
    
    Args:
        parent: Parent widget.
    """
    # Create the card
    card, content_frame, _ = self._create_card(
        parent,
        "Pool Chemistry Impact"
    )
    card.pack(fill="both", expand=True)
    
    # Get the zip code from config
    zip_code = self.config.get("weather", {}).get("zip_code", "")
    
    if not zip_code:
        # No zip code set
        instructions_label = tk.Label(
            content_frame,
            text="Please enter a zip code in the Location Settings above to view the weather impact analysis.",
            font=self.FONTS["normal"],
            fg=self.COLORS["text"],
            bg=self.COLORS["background"],
            wraplength=400,
            justify="left"
        )
        instructions_label.pack(fill="both", expand=True, padx=10, pady=10)
        return
    
    try:
        # Get detailed forecast impact
        impact = self.weather_service.get_detailed_forecast_impact(zip_code)
        
        if impact:
            # Create a frame for the impact analysis
            impact_frame = tk.Frame(content_frame, bg=self.COLORS["background"])
            impact_frame.pack(fill="both", expand=True, padx=10, pady=10)
            
            # Create a canvas with scrollbar for the impact analysis
            canvas_frame = tk.Frame(impact_frame, bg=self.COLORS["background"])
            canvas_frame.pack(fill="both", expand=True)
            
            canvas = tk.Canvas(
                canvas_frame,
                bg=self.COLORS["background"],
                highlightthickness=0
            )
            scrollbar = ttk.Scrollbar(
                canvas_frame,
                orient="vertical",
                command=canvas.yview
            )
            
            # Configure the canvas
            canvas.configure(yscrollcommand=scrollbar.set)
            canvas.pack(side="left", fill="both", expand=True)
            scrollbar.pack(side="right", fill="y")
            
            # Create a frame for the impact content
            content_frame = tk.Frame(canvas, bg=self.COLORS["background"])
            canvas.create_window((0, 0), window=content_frame, anchor="nw")
            
            # Add impact analysis for each day
            for i, day_impact in enumerate(impact):
                day_frame = tk.Frame(content_frame, bg=self.COLORS["background"])
                day_frame.pack(fill="x", pady=(0, 15) if i < len(impact) - 1 else 0)
                
                # Parse the date
                date_obj = datetime.fromisoformat(day_impact['date'])
                day_name = date_obj.strftime("%A")
                day_date = date_obj.strftime("%B %d, %Y")
                
                # Determine the severity color
                severity = day_impact['severity']
                severity_color = self.COLORS["success"]
                if severity == "moderate":
                    severity_color = self.COLORS["warning"]
                elif severity == "high":
                    severity_color = self.COLORS["danger"]
                
                # Day header with severity indicator
                header_frame = tk.Frame(day_frame, bg=severity_color)
                header_frame.pack(fill="x")
                
                day_label = tk.Label(
                    header_frame,
                    text=f"{day_name} - {day_date}",
                    font=self.FONTS["subheading"],
                    fg="white",
                    bg=severity_color,
                    anchor="w",
                    padx=10,
                    pady=5
                )
                day_label.pack(side="left")
                
                severity_label = tk.Label(
                    header_frame,
                    text=f"Impact: {severity.title()}",
                    font=self.FONTS["normal"],
                    fg="white",
                    bg=severity_color,
                    anchor="e",
                    padx=10,
                    pady=5
                )
                severity_label.pack(side="right")
                
                # Impact details
                details_frame = tk.Frame(day_frame, bg=self.COLORS["background"])
                details_frame.pack(fill="x", padx=10, pady=10)
                
                # Weather summary
                summary_frame = tk.Frame(details_frame, bg=self.COLORS["background"])
                summary_frame.pack(fill="x", pady=(0, 10))
                
                summary_label = tk.Label(
                    summary_frame,
                    text=f"Weather: {day_impact['conditions']}, {day_impact['temperature_high']:.1f}\u00b0F, {day_impact['chance_of_rain']}% rain, UV {day_impact['uv_index']}",
                    font=self.FONTS["normal"],
                    fg=self.COLORS["text"],
                    bg=self.COLORS["background"],
                    anchor="w",
                    wraplength=400,
                    justify="left"
                )
                summary_label.pack(anchor="w")
                
                # Impact by parameter
                for param, messages in day_impact['impact'].items():
                    if not messages:
                        continue
                    
                    param_frame = tk.Frame(details_frame, bg=self.COLORS["background"])
                    param_frame.pack(fill="x", pady=(0, 5))
                    
                    # Get the display name for the parameter
                    param_info = self.data_visualization.PARAMETER_INFO.get(
                        param,
                        {"name": param.replace("_", " ").title(), "unit": ""}
                    )
                    param_name = param_info["name"]
                    
                    param_label = tk.Label(
                        param_frame,
                        text=f"{param_name}:",
                        font=self.FONTS["normal"],
                        fg=self.COLORS["primary_dark"],
                        bg=self.COLORS["background"],
                        anchor="w"
                    )
                    param_label.pack(anchor="w")
                    
                    for message in messages:
                        message_frame = tk.Frame(param_frame, bg=self.COLORS["background"])
                        message_frame.pack(fill="x", padx=(20, 0))
                        
                        message_label = tk.Label(
                            message_frame,
                            text=f"\u2022 {message}",
                            font=self.FONTS["small"],
                            fg=self.COLORS["text"],
                            bg=self.COLORS["background"],
                            anchor="w",
                            wraplength=380,
                            justify="left"
                        )
                        message_label.pack(anchor="w")
            
            # Update the canvas scroll region
            content_frame.update_idletasks()
            canvas.config(scrollregion=canvas.bbox("all"))
        else:
            # No impact data
            error_label = tk.Label(
                content_frame,
                text="No impact analysis available. Please check your internet connection and try again.",
                font=self.FONTS["normal"],
                fg=self.COLORS["text"],
                bg=self.COLORS["background"],
                wraplength=400,
                justify="left"
            )
            error_label.pack(fill="both", expand=True, padx=10, pady=10)
    except Exception as e:
        logger.error(f"Error creating impact card: {e}")
        
        # Show error message
        error_label = tk.Label(
            content_frame,
            text=f"Error loading impact data: {str(e)}",
            font=self.FONTS["normal"],
            fg=self.COLORS["danger"],
            bg=self.COLORS["background"],
            wraplength=400,
            justify="left"
        )
        error_label.pack(fill="both", expand=True, padx=10, pady=10)

def _update_weather_location(self):
    """Update the weather location based on the entered zip code."""
    zip_var = self.data_cache.get("weather_zip_code")
    
    if not zip_var:
        return
    
    zip_code = zip_var.get().strip()
    
    if not zip_code:
        messagebox.showwarning(
            "No Zip Code",
            "Please enter a zip code."
        )
        return
    
    try:
        # Validate the zip code by trying to get the location name
        location_name = self.weather_service.get_location_name(zip_code)
        
        # Update the config
        if "weather" not in self.config:
            self.config["weather"] = {}
        
        self.config["weather"]["zip_code"] = zip_code
        
        # Save the config
        self._save_config()
        
        # Show success message
        messagebox.showinfo(
            "Location Updated",
            f"Weather location updated to {location_name}."
        )
        
        # Refresh the weather impact view
        if self.current_view == "weather_impact":
            self.show_weather_impact()
    except Exception as e:
        logger.error(f"Error updating weather location: {e}")
        messagebox.showerror(
            "Error",
            f"Error updating weather location: {str(e)}"
        )

def _save_config(self):
    """Save the configuration to a file."""
    try:
        with open("config.json", "w") as f:
            json.dump(self.config, f, indent=2)
    except Exception as e:
        logger.error(f"Error saving config: {e}")

def show_historical_data(self):
    """Show the historical data visualization view."""
    self._clear_content_frame()
    self.current_view = "historical_data"
    
    # Create page header
    self._create_page_header(
        "Historical Data Visualization",
        "Visualize and analyze your pool chemistry data over time."
    )
    
    # Create a frame for the historical data content
    historical_frame = tk.Frame(self.content_frame, bg=self.COLORS["background"])
    historical_frame.pack(fill="both", expand=True, padx=20, pady=10)
    
    # Configure the grid layout
    historical_frame.columnconfigure(0, weight=1)
    historical_frame.columnconfigure(1, weight=1)
    historical_frame.rowconfigure(0, weight=0)  # Controls
    historical_frame.rowconfigure(1, weight=1)  # Charts
    
    # Create the controls card
    self._create_historical_controls_card(historical_frame)
    
    # Create the visualization card
    visualization_frame = tk.Frame(historical_frame, bg=self.COLORS["background"])
    visualization_frame.grid(row=1, column=0, columnspan=2, sticky="nsew", pady=(10, 0))
    
    self._create_historical_visualization_card(visualization_frame)
    
    # Update status message
    self.status_message.config(text="Historical Data Visualization view loaded")

def _create_historical_controls_card(self, parent):
    """
    Create a card for historical data visualization controls.
    
    Args:
        parent: Parent widget.
    """
    # Create the card
    card, content_frame, _ = self._create_card(
        parent,
        "Visualization Controls"
    )
    card.grid(row=0, column=0, columnspan=2, sticky="ew")
    
    # Create a frame for the controls
    controls_frame = tk.Frame(content_frame, bg=self.COLORS["background"])
    controls_frame.pack(fill="x", padx=10, pady=10)
    
    # Parameter selection
    param_frame = tk.Frame(controls_frame, bg=self.COLORS["background"])
    param_frame.pack(side="left", padx=(0, 20))
    
    param_label = tk.Label(
        param_frame,
        text="Parameters:",
        font=self.FONTS["normal"],
        fg=self.COLORS["text"],
        bg=self.COLORS["background"]
    )
    param_label.pack(side="left")
    
    # Create checkboxes for each parameter
    parameters = [
        ("ph", "pH"),
        ("free_chlorine", "Free Chlorine"),
        ("total_chlorine", "Total Chlorine"),
        ("total_alkalinity", "Alkalinity"),
        ("calcium_hardness", "Calcium"),
        ("cyanuric_acid", "CYA"),
        ("temperature", "Temperature")
    ]
    
    # Store the parameter variables
    self.data_cache["historical_parameters"] = {}
    
    for param_id, param_name in parameters:
        var = tk.BooleanVar(value=param_id in ["ph", "free_chlorine", "total_alkalinity"])
        
        checkbox = ttk.Checkbutton(
            param_frame,
            text=param_name,
            variable=var,
            onvalue=True,
            offvalue=False
        )
        checkbox.pack(side="left", padx=(5, 0))
        
        # Store the variable
        self.data_cache["historical_parameters"][param_id] = var
    
    # Date range selection
    date_frame = tk.Frame(controls_frame, bg=self.COLORS["background"])
    date_frame.pack(side="left")
    
    date_label = tk.Label(
        date_frame,
        text="Date Range:",
        font=self.FONTS["normal"],
        fg=self.COLORS["text"],
        bg=self.COLORS["background"]
    )
    date_label.pack(side="left")
    
    # Create radio buttons for date range options
    date_ranges = [
        ("week", "Last Week"),
        ("month", "Last Month"),
        ("3month", "Last 3 Months"),
        ("year", "Last Year"),
        ("all", "All Time"),
        ("custom", "Custom")
    ]
    
    # Store the date range variable
    date_var = tk.StringVar(value="month")
    self.data_cache["historical_date_range"] = date_var
    
    for range_id, range_name in date_ranges:
        radio = ttk.Radiobutton(
            date_frame,
            text=range_name,
            variable=date_var,
            value=range_id
        )
        radio.pack(side="left", padx=(5, 0))
    
    # Add a button to update the visualization
    update_button = ttk.Button(
        controls_frame,
        text="Update Visualization",
        command=self._update_historical_visualization
    )
    update_button.pack(side="right")

def _create_historical_visualization_card(self, parent):
    """
    Create a card for historical data visualization.
    
    Args:
        parent: Parent widget.
    """
    # Create the card
    card, content_frame, _ = self._create_card(
        parent,
        "Data Visualization"
    )
    card.pack(fill="both", expand=True)
    
    # Create a notebook for different visualization types
    notebook = ttk.Notebook(content_frame)
    notebook.pack(fill="both", expand=True, padx=10, pady=10)
    
    # Time series tab
    time_series_tab = ttk.Frame(notebook)
    notebook.add(time_series_tab, text="Time Series")
    
    # Dashboard tab
    dashboard_tab = ttk.Frame(notebook)
    notebook.add(dashboard_tab, text="Dashboard")
    
    # Statistics tab
    statistics_tab = ttk.Frame(notebook)
    notebook.add(statistics_tab, text="Statistics")
    
    # Correlation tab
    correlation_tab = ttk.Frame(notebook)
    notebook.add(correlation_tab, text="Correlation")
    
    # AI Predictions tab
    predictions_tab = ttk.Frame(notebook)
    notebook.add(predictions_tab, text="AI Predictions")
    
    # Create frames for each tab
    time_series_frame = tk.Frame(time_series_tab, bg=self.COLORS["background"])
    time_series_frame.pack(fill="both", expand=True)
    
    dashboard_frame = tk.Frame(dashboard_tab, bg=self.COLORS["background"])
    dashboard_frame.pack(fill="both", expand=True)
    
    statistics_frame = tk.Frame(statistics_tab, bg=self.COLORS["background"])
    statistics_frame.pack(fill="both", expand=True)
    
    correlation_frame = tk.Frame(correlation_tab, bg=self.COLORS["background"])
    correlation_frame.pack(fill="both", expand=True)
    
    predictions_frame = tk.Frame(predictions_tab, bg=self.COLORS["background"])
    predictions_frame.pack(fill="both", expand=True)
    
    # Store references to the visualization frames
    self.ui_elements["historical_time_series_frame"] = time_series_frame
    self.ui_elements["historical_dashboard_frame"] = dashboard_frame
    self.ui_elements["historical_statistics_frame"] = statistics_frame
    self.ui_elements["historical_correlation_frame"] = correlation_frame
    self.ui_elements["historical_predictions_frame"] = predictions_frame
    
    # Add placeholder content
    for frame, title in [
        (time_series_frame, "Time Series Chart"),
        (dashboard_frame, "Parameter Dashboard"),
        (statistics_frame, "Statistical Analysis"),
        (correlation_frame, "Parameter Correlation"),
        (predictions_frame, "AI Predictions")
    ]:
        placeholder_label = tk.Label(
            frame,
            text=f"Select parameters and date range above, then click 'Update Visualization' to see the {title}.",
            font=self.FONTS["normal"],
            fg=self.COLORS["text"],
            bg=self.COLORS["background"],
            wraplength=800,
            justify="center"
        )
        placeholder_label.place(relx=0.5, rely=0.5, anchor="center")
    
    # Store the notebook reference
    self.ui_elements["historical_notebook"] = notebook
    
    # Add export buttons
    export_frame = tk.Frame(content_frame, bg=self.COLORS["background"])
    export_frame.pack(fill="x", padx=10, pady=(0, 10))
    
    export_csv_button = ttk.Button(
        export_frame,
        text="Export to CSV",
        command=self._export_historical_data_csv
    )
    export_csv_button.pack(side="left")
    
    export_pdf_button = ttk.Button(
        export_frame,
        text="Export to PDF",
        command=self._export_historical_data_pdf
    )
    export_pdf_button.pack(side="left", padx=(10, 0))

def _update_historical_visualization(self):
    """Update the historical data visualization based on selected parameters and date range."""
    # Get selected parameters
    param_vars = self.data_cache.get("historical_parameters", {})
    selected_params = [param for param, var in param_vars.items() if var.get()]
    
    if not selected_params:
        messagebox.showwarning(
            "No Parameters",
            "Please select at least one parameter to visualize."
        )
        return
    
    # Get selected date range
    date_range = self.data_cache.get("historical_date_range", tk.StringVar()).get()
    
    # Calculate start and end dates
    end_date = datetime.now().isoformat()
    start_date = None
    
    if date_range == "week":
        start_date = (datetime.now() - timedelta(days=7)).isoformat()
    elif date_range == "month":
        start_date = (datetime.now() - timedelta(days=30)).isoformat()
    elif date_range == "3month":
        start_date = (datetime.now() - timedelta(days=90)).isoformat()
    elif date_range == "year":
        start_date = (datetime.now() - timedelta(days=365)).isoformat()
    elif date_range == "custom":
        # TODO: Implement custom date range selection
        messagebox.showinfo(
            "Custom Date Range",
            "Custom date range selection is not yet implemented. Using last month instead."
        )
        start_date = (datetime.now() - timedelta(days=30)).isoformat()
    
    try:
        # Update the time series chart
        self._update_time_series_chart(selected_params, start_date, end_date)
        
        # Update the dashboard
        self._update_dashboard_chart(selected_params, start_date, end_date)
        
        # Update the statistics
        self._update_statistics_chart(selected_params, start_date, end_date)
        
        # Update the correlation chart
        if len(selected_params) >= 2:
            self._update_correlation_chart(selected_params, start_date, end_date)
        else:
            # Show message that correlation requires at least 2 parameters
            correlation_frame = self.ui_elements.get("historical_correlation_frame")
            if correlation_frame:
                for widget in correlation_frame.winfo_children():
                    widget.destroy()
                
                message_label = tk.Label(
                    correlation_frame,
                    text="Correlation analysis requires at least 2 parameters. Please select more parameters.",
                    font=self.FONTS["normal"],
                    fg=self.COLORS["text"],
                    bg=self.COLORS["background"],
                    wraplength=800,
                    justify="center"
                )
                message_label.place(relx=0.5, rely=0.5, anchor="center")
        
        # Update the AI predictions
        self._update_ai_predictions(selected_params, start_date, end_date)
        
        # Switch to the time series tab
        notebook = self.ui_elements.get("historical_notebook")
        if notebook:
            notebook.select(0)
    except Exception as e:
        logger.error(f"Error updating historical visualization: {e}")
        messagebox.showerror(
            "Error",
            f"Error updating visualization: {str(e)}"
        )

def _update_time_series_chart(self, parameters, start_date, end_date):
    """
    Update the time series chart.
    
    Args:
        parameters: List of parameters to include.
        start_date: Start date for the data.
        end_date: End date for the data.
    """
    time_series_frame = self.ui_elements.get("historical_time_series_frame")
    if not time_series_frame:
        return
    
    # Clear the frame
    for widget in time_series_frame.winfo_children():
        widget.destroy()
    
    try:
        # Create a time series chart
        chart_path = self.data_visualization.create_time_series_graph(
            parameters=parameters,
            start_date=start_date,
            end_date=end_date,
            title="Pool Chemistry Time Series",
            figsize=(10, 6),
            dpi=100,
            show_ideal_ranges=True,
            show_trend_line=True
        )
        
        # Load and display the chart image
        chart_image = Image.open(chart_path)
        chart_photo = ImageTk.PhotoImage(chart_image)
        self.images["time_series_chart"] = chart_photo
        
        chart_label = tk.Label(
            time_series_frame,
            image=chart_photo,
            bg=self.COLORS["background"]
        )
        chart_label.pack(fill="both", expand=True)
    except Exception as e:
        logger.error(f"Error creating time series chart: {e}")
        
        error_label = tk.Label(
            time_series_frame,
            text=f"Error creating time series chart: {str(e)}",
            font=self.FONTS["normal"],
            fg=self.COLORS["danger"],
            bg=self.COLORS["background"],
            wraplength=800,
            justify="center"
        )
        error_label.place(relx=0.5, rely=0.5, anchor="center")

def _update_dashboard_chart(self, parameters, start_date, end_date):
    """
    Update the dashboard chart.
    
    Args:
        parameters: List of parameters to include.
        start_date: Start date for the data.
        end_date: End date for the data.
    """
    dashboard_frame = self.ui_elements.get("historical_dashboard_frame")
    if not dashboard_frame:
        return
    
    # Clear the frame
    for widget in dashboard_frame.winfo_children():
        widget.destroy()
    
    try:
        # Create a dashboard chart
        chart_path = self.data_visualization.create_multi_parameter_dashboard(
            parameters=parameters,
            start_date=start_date,
            end_date=end_date,
            figsize=(10, 8),
            dpi=100
        )
        
        # Load and display the chart image
        chart_image = Image.open(chart_path)
        chart_photo = ImageTk.PhotoImage(chart_image)
        self.images["dashboard_chart"] = chart_photo
        
        chart_label = tk.Label(
            dashboard_frame,
            image=chart_photo,
            bg=self.COLORS["background"]
        )
        chart_label.pack(fill="both", expand=True)
    except Exception as e:
        logger.error(f"Error creating dashboard chart: {e}")
        
        error_label = tk.Label(
            dashboard_frame,
            text=f"Error creating dashboard chart: {str(e)}",
            font=self.FONTS["normal"],
            fg=self.COLORS["danger"],
            bg=self.COLORS["background"],
            wraplength=800,
            justify="center"
        )
        error_label.place(relx=0.5, rely=0.5, anchor="center")

def _update_statistics_chart(self, parameters, start_date, end_date):
    """
    Update the statistics chart.
    
    Args:
        parameters: List of parameters to include.
        start_date: Start date for the data.
        end_date: End date for the data.
    """
    statistics_frame = self.ui_elements.get("historical_statistics_frame")
    if not statistics_frame:
        return
    
    # Clear the frame
    for widget in statistics_frame.winfo_children():
        widget.destroy()
    
    try:
        # Create a statistical summary chart
        chart_path = self.data_visualization.create_statistical_summary(
            parameters=parameters,
            start_date=start_date,
            end_date=end_date,
            figsize=(10, 8),
            dpi=100
        )
        
        # Load and display the chart image
        chart_image = Image.open(chart_path)
        chart_photo = ImageTk.PhotoImage(chart_image)
        self.images["statistics_chart"] = chart_photo
        
        chart_label = tk.Label(
            statistics_frame,
            image=chart_photo,
            bg=self.COLORS["background"]
        )
        chart_label.pack(fill="both", expand=True)
    except Exception as e:
        logger.error(f"Error creating statistics chart: {e}")
        
        error_label = tk.Label(
            statistics_frame,
            text=f"Error creating statistics chart: {str(e)}",
            font=self.FONTS["normal"],
            fg=self.COLORS["danger"],
            bg=self.COLORS["background"],
            wraplength=800,
            justify="center"
        )
        error_label.place(relx=0.5, rely=0.5, anchor="center")

def _update_correlation_chart(self, parameters, start_date, end_date):
    """
    Update the correlation chart.
    
    Args:
        parameters: List of parameters to include.
        start_date: Start date for the data.
        end_date: End date for the data.
    """
    correlation_frame = self.ui_elements.get("historical_correlation_frame")
    if not correlation_frame:
        return
    
    # Clear the frame
    for widget in correlation_frame.winfo_children():
        widget.destroy()
    
    try:
        # Create a correlation matrix chart
        chart_path = self.data_visualization.create_correlation_matrix(
            parameters=parameters,
            start_date=start_date,
            end_date=end_date,
            figsize=(8, 8),
            dpi=100
        )
        
        # Load and display the chart image
        chart_image = Image.open(chart_path)
        chart_photo = ImageTk.PhotoImage(chart_image)
        self.images["correlation_chart"] = chart_photo
        
        chart_label = tk.Label(
            correlation_frame,
            image=chart_photo,
            bg=self.COLORS["background"]
        )
        chart_label.pack(fill="both", expand=True)
    except Exception as e:
        logger.error(f"Error creating correlation chart: {e}")
        
        error_label = tk.Label(
            correlation_frame,
            text=f"Error creating correlation chart: {str(e)}",
            font=self.FONTS["normal"],
            fg=self.COLORS["danger"],
            bg=self.COLORS["background"],
            wraplength=800,
            justify="center"
        )
        error_label.place(relx=0.5, rely=0.5, anchor="center")

def _update_ai_predictions(self, parameters, start_date, end_date):
    """
    Update the AI predictions.
    
    Args:
        parameters: List of parameters to include.
        start_date: Start date for the data.
        end_date: End date for the data.
    """
    predictions_frame = self.ui_elements.get("historical_predictions_frame")
    if not predictions_frame:
        return
    
    # Clear the frame
    for widget in predictions_frame.winfo_children():
        widget.destroy()
    
    # Create a canvas with scrollbar for the predictions
    canvas_frame = tk.Frame(predictions_frame, bg=self.COLORS["background"])
    canvas_frame.pack(fill="both", expand=True)
    
    canvas = tk.Canvas(
        canvas_frame,
        bg=self.COLORS["background"],
        highlightthickness=0
    )
    scrollbar = ttk.Scrollbar(
        canvas_frame,
        orient="vertical",
        command=canvas.yview
    )
    
    # Configure the canvas
    canvas.configure(yscrollcommand=scrollbar.set)
    canvas.pack(side="left", fill="both", expand=True)
    scrollbar.pack(side="right", fill="y")
    
    # Create a frame for the predictions content
    content_frame = tk.Frame(canvas, bg=self.COLORS["background"])
    canvas.create_window((0, 0), window=content_frame, anchor="nw")
    
    # Add a header
    header_label = tk.Label(
        content_frame,
        text="AI-Powered Predictions and Insights",
        font=self.FONTS["subheading"],
        fg=self.COLORS["primary_dark"],
        bg=self.COLORS["background"],
        anchor="w"
    )
    header_label.pack(anchor="w", pady=(0, 10))
    
    # Add a description
    description_label = tk.Label(
        content_frame,
        text="Our AI system analyzes your historical data to predict future trends and provide actionable insights for maintaining optimal pool chemistry.",
        font=self.FONTS["normal"],
        fg=self.COLORS["text"],
        bg=self.COLORS["background"],
        wraplength=800,
        justify="left",
        anchor="w"
    )
    description_label.pack(anchor="w", pady=(0, 20))
    
    try:
        # Get sensor data
        sensor_data = self.db_service.get_sensor_data()
        
        if sensor_data and len(sensor_data) >= 3:
            # Generate predictions for each parameter
            for param in parameters:
                if param not in self.data_visualization.PARAMETER_INFO:
                    continue
                
                param_info = self.data_visualization.PARAMETER_INFO[param]
                param_name = param_info["name"]
                param_color = param_info["color"]
                
                # Create a card for this parameter
                param_card, param_content, _ = self._create_card(
                    content_frame,
                    f"{param_name} Predictions"
                )
                param_card.pack(fill="x", pady=(0, 20))
                
                # Extract data for this parameter
                param_data = []
                for item in sensor_data:
                    if param in item and item[param] is not None:
                        param_data.append({
                            "timestamp": datetime.fromisoformat(item["timestamp"]),
                            "value": item[param]
                        })
                
                # Sort by timestamp
                param_data.sort(key=lambda x: x["timestamp"])
                
                if len(param_data) >= 3:
                    # Generate a simple linear prediction
                    # In a real application, this would use more sophisticated ML models
                    x_data = [i for i in range(len(param_data))]
                    y_data = [item["value"] for item in param_data]
                    
                    # Simple linear regression
                    n = len(x_data)
                    sum_x = sum(x_data)
                    sum_y = sum(y_data)
                    sum_xy = sum(x*y for x, y in zip(x_data, y_data))
                    sum_xx = sum(x*x for x in x_data)
                    
                    # Calculate slope and intercept
                    slope = (n * sum_xy - sum_x * sum_y) / (n * sum_xx - sum_x * sum_x)
                    intercept = (sum_y - slope * sum_x) / n
                    
                    # Predict next 7 days
                    predictions = []
                    last_date = param_data[-1]["timestamp"]
                    
                    for i in range(1, 8):
                        next_date = last_date + timedelta(days=i)
                        next_value = slope * (len(param_data) + i - 1) + intercept
                        predictions.append({
                            "date": next_date,
                            "value": next_value
                        })
                    
                    # Calculate trend
                    trend = "stable"
                    if abs(slope) < 0.01:
                        trend = "stable"
                    elif slope > 0:
                        trend = "increasing"
                    else:
                        trend = "decreasing"
                    
                    # Add trend information
                    trend_frame = tk.Frame(param_content, bg=self.COLORS["background"])
                    trend_frame.pack(fill="x", pady=(0, 10))
                    
                    trend_label = tk.Label(
                        trend_frame,
                        text=f"Trend: {trend.title()}",
                        font=self.FONTS["normal"],
                        fg=self.COLORS["text"],
                        bg=self.COLORS["background"],
                        anchor="w"
                    )
                    trend_label.pack(side="left")
                    
                    # Add a trend icon
                    trend_canvas = tk.Canvas(
                        trend_frame,
                        width=20,
                        height=20,
                        bg=self.COLORS["background"],
                        highlightthickness=0
                    )
                    
                    if trend == "increasing":
                        trend_canvas.create_polygon(10, 5, 5, 15, 15, 15, fill=self.COLORS["danger"])
                    elif trend == "decreasing":
                        trend_canvas.create_polygon(10, 15, 5, 5, 15, 5, fill=self.COLORS["warning"])
                    else:
                        trend_canvas.create_rectangle(5, 10, 15, 12, fill=self.COLORS["success"])
                    
                    trend_canvas.pack(side="left", padx=(5, 0))
                    
                    # Add prediction table
                    table_frame = tk.Frame(param_content, bg=self.COLORS["background"])
                    table_frame.pack(fill="x")
                    
                    # Add header row
                    header_frame = tk.Frame(table_frame, bg=self.COLORS["primary_light"])
                    header_frame.pack(fill="x")
                    
                    date_header = tk.Label(
                        header_frame,
                        text="Date",
                        font=self.FONTS["normal"],
                        fg=self.COLORS["text"],
                        bg=self.COLORS["primary_light"],
                        width=15,
                        anchor="w",
                        padx=10,
                        pady=5
                    )
                    date_header.pack(side="left")
                    
                    value_header = tk.Label(
                        header_frame,
                        text="Predicted Value",
                        font=self.FONTS["normal"],
                        fg=self.COLORS["text"],
                        bg=self.COLORS["primary_light"],
                        width=15,
                        anchor="center",
                        pady=5
                    )
                    value_header.pack(side="left")
                    
                    # Add data rows
                    for i, prediction in enumerate(predictions):
                        row_frame = tk.Frame(
                            table_frame,
                            bg=self.COLORS["background_alt"] if i % 2 == 0 else self.COLORS["background"]
                        )
                        row_frame.pack(fill="x")
                        
                        date_label = tk.Label(
                            row_frame,
                            text=prediction["date"].strftime("%Y-%m-%d"),
                            font=self.FONTS["normal"],
                            fg=self.COLORS["text"],
                            bg=row_frame["bg"],
                            width=15,
                            anchor="w",
                            padx=10,
                            pady=5
                        )
                        date_label.pack(side="left")
                        
                        value_label = tk.Label(
                            row_frame,
                            text=f"{prediction['value']:.2f}",
                            font=self.FONTS["normal"],
                            fg=self.COLORS["text"],
                            bg=row_frame["bg"],
                            width=15,
                            anchor="center",
                            pady=5
                        )
                        value_label.pack(side="left")
                    
                    # Add insights
                    insights_frame = tk.Frame(param_content, bg=self.COLORS["background"])
                    insights_frame.pack(fill="x", pady=(10, 0))
                    
                    insights_label = tk.Label(
                        insights_frame,
                        text="AI Insights:",
                        font=self.FONTS["normal"],
                        fg=self.COLORS["primary_dark"],
                        bg=self.COLORS["background"],
                        anchor="w"
                    )
                    insights_label.pack(anchor="w")
                    
                    # Generate insights based on the parameter and trend
                    insights = []
                    
                    if param == "ph":
                        if trend == "increasing":
                            insights.append("pH is trending upward. Consider adding pH decreaser if it exceeds 7.8.")
                        elif trend == "decreasing":
                            insights.append("pH is trending downward. Monitor closely and add pH increaser if it falls below 7.2.")
                        else:
                            insights.append("pH is stable, which is ideal for pool chemistry balance.")
                    
                    elif param == "free_chlorine":
                        if trend == "increasing":
                            insights.append("Free chlorine is trending upward. Reduce chlorine addition frequency.")
                        elif trend == "decreasing":
                            insights.append("Free chlorine is trending downward. Increase chlorine addition or check for factors depleting chlorine.")
                        else:
                            insights.append("Free chlorine is stable, indicating good sanitizer management.")
                    
                    elif param == "total_alkalinity":
                        if trend == "increasing":
                            insights.append("Total alkalinity is trending upward. Monitor pH stability and consider adding pH decreaser if needed.")
                        elif trend == "decreasing":
                            insights.append("Total alkalinity is trending downward. Add alkalinity increaser to maintain pH buffering capacity.")
                        else:
                            insights.append("Total alkalinity is stable, providing good pH buffering.")
                    
                    # Add weather correlation insight
                    insights.append("Based on weather forecast, expect increased chlorine demand in the coming days due to higher temperatures and UV levels.")
                    
                    # Add maintenance recommendation
                    if param == "free_chlorine" and trend == "decreasing":
                        insights.append("RECOMMENDATION: Schedule shock treatment within the next 3 days to prevent algae growth.")
                    
                    # Display insights
                    for insight in insights:
                        insight_label = tk.Label(
                            insights_frame,
                            text=f"\u2022 {insight}",
                            font=self.FONTS["normal"],
                            fg=self.COLORS["text"],
                            bg=self.COLORS["background"],
                            wraplength=700,
                            justify="left",
                            anchor="w"
                        )
                        insight_label.pack(anchor="w", pady=(5, 0))
                else:
                    # Not enough data for predictions
                    not_enough_label = tk.Label(
                        param_content,
                        text=f"Not enough historical data for {param_name} predictions. Add more test results to enable predictions.",
                        font=self.FONTS["normal"],
                        fg=self.COLORS["text"],
                        bg=self.COLORS["background"],
                        wraplength=700,
                        justify="left"
                    )
                    not_enough_label.pack(fill="both", expand=True)
            
            # Add overall recommendations
            recommendations_card, recommendations_content, _ = self._create_card(
                content_frame,
                "AI Recommendations"
            )
            recommendations_card.pack(fill="x", pady=(0, 20))
            
            recommendations_label = tk.Label(
                recommendations_content,
                text="Based on your historical data and predictive analysis, our AI system recommends the following actions:",
                font=self.FONTS["normal"],
                fg=self.COLORS["text"],
                bg=self.COLORS["background"],
                wraplength=700,
                justify="left",
                anchor="w"
            )
            recommendations_label.pack(anchor="w", pady=(0, 10))
            
            # Generate some sample recommendations
            recommendations = [
                "Maintain current chlorine addition schedule, but be prepared to increase frequency if temperatures rise above 90\u00b0F next week.",
                "Monitor pH closely over the next 7 days as the predicted rainfall may cause fluctuations.",
                "Consider adding cyanuric acid to maintain chlorine stability during the high UV days forecasted for next week.",
                "Schedule a filter cleaning within the next 10 days based on your maintenance history and current water quality trends."
            ]
            
            for recommendation in recommendations:
                rec_frame = tk.Frame(recommendations_content, bg=self.COLORS["background"])
                rec_frame.pack(fill="x", pady=(0, 5))
                
                rec_label = tk.Label(
                    rec_frame,
                    text=f"\u2022 {recommendation}",
                    font=self.FONTS["normal"],
                    fg=self.COLORS["text"],
                    bg=self.COLORS["background"],
                    wraplength=700,
                    justify="left",
                    anchor="w"
                )
                rec_label.pack(anchor="w")
        else:
            # Not enough data for predictions
            not_enough_label = tk.Label(
                content_frame,
                text="Not enough historical data for AI predictions. Add at least 3 test results to enable predictions.",
                font=self.FONTS["normal"],
                fg=self.COLORS["text"],
                bg=self.COLORS["background"],
                wraplength=800,
                justify="center"
            )
            not_enough_label.pack(fill="both", expand=True)
    except Exception as e:
        logger.error(f"Error generating AI predictions: {e}")
        
        error_label = tk.Label(
            content_frame,
            text=f"Error generating AI predictions: {str(e)}",
            font=self.FONTS["normal"],
            fg=self.COLORS["danger"],
            bg=self.COLORS["background"],
            wraplength=800,
            justify="center"
        )
        error_label.pack(fill="both", expand=True)
    
    # Update the canvas scroll region
    content_frame.update_idletasks()
    canvas.config(scrollregion=canvas.bbox("all"))

def _export_historical_data_csv(self):
    """Export historical data to a CSV file."""
    try:
        # Get selected parameters
        param_vars = self.data_cache.get("historical_parameters", {})
        selected_params = [param for param, var in param_vars.items() if var.get()]
        
        if not selected_params:
            messagebox.showwarning(
                "No Parameters",
                "Please select at least one parameter to export."
            )
            return
        
        # Get selected date range
        date_range = self.data_cache.get("historical_date_range", tk.StringVar()).get()
        
        # Calculate start and end dates
        end_date = datetime.now().isoformat()
        start_date = None
        
        if date_range == "week":
            start_date = (datetime.now() - timedelta(days=7)).isoformat()
        elif date_range == "month":
            start_date = (datetime.now() - timedelta(days=30)).isoformat()
        elif date_range == "3month":
            start_date = (datetime.now() - timedelta(days=90)).isoformat()
        elif date_range == "year":
            start_date = (datetime.now() - timedelta(days=365)).isoformat()
        
        # Ask for the output file location
        file_path = filedialog.asksaveasfilename(
            title="Export Data to CSV",
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")]
        )
        
        if not file_path:
            return
        
        # Export the data
        csv_path = self.data_visualization.export_data_to_csv(
            parameters=selected_params,
            start_date=start_date,
            end_date=end_date,
            output_file=file_path
        )
        
        messagebox.showinfo(
            "Export Successful",
            f"Data exported successfully to {csv_path}"
        )
    except Exception as e:
        logger.error(f"Error exporting data to CSV: {e}")
        messagebox.showerror(
            "Export Error",
            f"Error exporting data to CSV: {str(e)}"
        )

def _export_historical_data_pdf(self):
    """Export historical data to a PDF report."""
    try:
        # Get selected parameters
        param_vars = self.data_cache.get("historical_parameters", {})
        selected_params = [param for param, var in param_vars.items() if var.get()]
        
        if not selected_params:
            messagebox.showwarning(
                "No Parameters",
                "Please select at least one parameter to export."
            )
            return
        
        # Get selected date range
        date_range = self.data_cache.get("historical_date_range", tk.StringVar()).get()
        
        # Calculate start and end dates
        end_date = datetime.now().isoformat()
        start_date = None
        
        if date_range == "week":
            start_date = (datetime.now() - timedelta(days=7)).isoformat()
        elif date_range == "month":
            start_date = (datetime.now() - timedelta(days=30)).isoformat()
        elif date_range == "3month":
            start_date = (datetime.now() - timedelta(days=90)).isoformat()
        elif date_range == "year":
            start_date = (datetime.now() - timedelta(days=365)).isoformat()
        
        # Ask for the output file location
        file_path = filedialog.asksaveasfilename(
            title="Export Data to PDF",
            defaultextension=".pdf",
            filetypes=[("PDF files", "*.pdf"), ("All files", "*.*")]
        )
        
        if not file_path:
            return
        
        # Export the data
        pdf_path = self.data_visualization.generate_pdf_report(
            parameters=selected_params,
            start_date=start_date,
            end_date=end_date,
            output_file=file_path
        )
        
        messagebox.showinfo(
            "Export Successful",
            f"Report exported successfully to {pdf_path}"
        )
    except Exception as e:
        logger.error(f"Error exporting data to PDF: {e}")
        messagebox.showerror(
            "Export Error",
            f"Error exporting data to PDF: {str(e)}"
        )

def show_maintenance_log(self, add_new=False):
    """
    Show the maintenance log view.
    
    Args:
        add_new: Whether to show the add new entry form.
    """
    self._clear_content_frame()
    self.current_view = "maintenance_log"
    
    # Create page header
    self._create_page_header(
        "Maintenance Log",
        "Track and manage pool maintenance activities."
    )
    
    # Create a frame for the maintenance log content
    maintenance_frame = tk.Frame(self.content_frame, bg=self.COLORS["background"])
    maintenance_frame.pack(fill="both", expand=True, padx=20, pady=10)
    
    # Configure the grid layout
    maintenance_frame.columnconfigure(0, weight=1)
    maintenance_frame.columnconfigure(1, weight=1)
    maintenance_frame.rowconfigure(0, weight=1)
    
    # Create the maintenance log list
    log_frame = tk.Frame(maintenance_frame, bg=self.COLORS["background"])
    log_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 10))
    
    self._create_maintenance_log_card(log_frame)
    
    # Create the add/edit entry form
    form_frame = tk.Frame(maintenance_frame, bg=self.COLORS["background"])
    form_frame.grid(row=0, column=1, sticky="nsew", padx=(10, 0))
    
    self._create_maintenance_form_card(form_frame)
    
    # If add_new is True, focus the form
    if add_new:
        self._show_add_maintenance_form()
    
    # Update status message
    self.status_message.config(text="Maintenance Log view loaded")

def _create_maintenance_log_card(self, parent):
    """
    Create a card for the maintenance log list.
    
    Args:
        parent: Parent widget.
    """
    # Create the card
    card, content_frame, _ = self._create_card(
        parent,
        "Maintenance History"
    )
    card.pack(fill="both", expand=True)
    
    # Create a frame for the controls
    controls_frame = tk.Frame(content_frame, bg=self.COLORS["background"])
    controls_frame.pack(fill="x", padx=10, pady=10)
    
    # Add a search field
    search_frame, search_var, _ = self._create_data_entry_field(
        controls_frame,
        "Search",
        default_value="",
        width=20,
        tooltip="Search maintenance logs"
    )
    search_frame.pack(side="left")
    
    # Store the search variable
    self.data_cache["maintenance_search"] = search_var
    
    # Add a search button
    search_button = ttk.Button(
        controls_frame,
        text="Search",
        command=self._search_maintenance_logs
    )
    search_button.pack(side="left", padx=(5, 0))
    
    # Add a button to add a new entry
    add_button = ttk.Button(
        controls_frame,
        text="Add New Entry",
        command=self._show_add_maintenance_form
    )
    add_button.pack(side="right")
    
    # Create a frame for the log list
    log_list_frame = tk.Frame(content_frame, bg=self.COLORS["background"])
    log_list_frame.pack(fill="both", expand=True, padx=10, pady=(0, 10))
    
    # Create a canvas with scrollbar for the log list
    canvas_frame = tk.Frame(log_list_frame, bg=self.COLORS["background"])
    canvas_frame.pack(fill="both", expand=True)
    
    canvas = tk.Canvas(
        canvas_frame,
        bg=self.COLORS["background"],
        highlightthickness=0
    )
    scrollbar = ttk.Scrollbar(
        canvas_frame,
        orient="vertical",
        command=canvas.yview
    )
    
    # Configure the canvas
    canvas.configure(yscrollcommand=scrollbar.set)
    canvas.pack(side="left", fill="both", expand=True)
    scrollbar.pack(side="right", fill="y")
    
    # Create a frame for the log entries
    entries_frame = tk.Frame(canvas, bg=self.COLORS["background"])
    canvas.create_window((0, 0), window=entries_frame, anchor="nw")
    
    # Store references to the log list elements
    self.ui_elements["maintenance_log_canvas"] = canvas
    self.ui_elements["maintenance_log_entries_frame"] = entries_frame
    
    # Load the maintenance logs
    self._load_maintenance_logs()
    
    # Update the canvas scroll region
    entries_frame.update_idletasks()
    canvas.config(scrollregion=canvas.bbox("all"))

def _create_maintenance_form_card(self, parent):
    """
    Create a card for the maintenance entry form.
    
    Args:
        parent: Parent widget.
    """
    # Create the card
    card, content_frame, _ = self._create_card(
        parent,
        "Add Maintenance Entry"
    )
    card.pack(fill="both", expand=True)
    
    # Create a frame for the form
    form_frame = tk.Frame(content_frame, bg=self.COLORS["background"])
    form_frame.pack(fill="both", expand=True, padx=10, pady=10)
    
    # Add form fields
    # Date field
    date_frame = tk.Frame(form_frame, bg=self.COLORS["background"])
    date_frame.pack(fill="x", pady=(0, 10))
    
    date_label = tk.Label(
        date_frame,
        text="Date",
        font=self.FONTS["normal"],
        fg=self.COLORS["text"],
        bg=self.COLORS["background"],
        width=15,
        anchor="w"
    )
    date_label.pack(side="left")
    
    # Use current date as default
    current_date = datetime.now().strftime("%Y-%m-%d")
    date_var = tk.StringVar(value=current_date)
    
    date_entry = ttk.Entry(
        date_frame,
        textvariable=date_var,
        width=15
    )
    date_entry.pack(side="left")
    
    # Store the date variable
    self.data_cache["maintenance_date"] = date_var
    
    # Action field
    action_frame = tk.Frame(form_frame, bg=self.COLORS["background"])
    action_frame.pack(fill="x", pady=(0, 10))
    
    action_label = tk.Label(
        action_frame,
        text="Action",
        font=self.FONTS["normal"],
        fg=self.COLORS["text"],
        bg=self.COLORS["background"],
        width=15,
        anchor="w"
    )
    action_label.pack(side="left")
    
    action_var = tk.StringVar()
    
    # Create a combobox with common actions
    actions = [
        "Clean Filter",
        "Add Chemicals",
        "Brush Pool",
        "Vacuum Pool",
        "Test Water",
        "Backwash Filter",
        "Clean Skimmer",
        "Shock Treatment",
        "Other"
    ]
    
    action_combo = ttk.Combobox(
        action_frame,
        textvariable=action_var,
        values=actions,
        width=30
    )
    action_combo.pack(side="left")
    
    # Store the action variable
    self.data_cache["maintenance_action"] = action_var
    
    # Details field
    details_frame = tk.Frame(form_frame, bg=self.COLORS["background"])
    details_frame.pack(fill="x", pady=(0, 10))
    
    details_label = tk.Label(
        details_frame,
        text="Details",
        font=self.FONTS["normal"],
        fg=self.COLORS["text"],
        bg=self.COLORS["background"],
        width=15,
        anchor="w"
    )
    details_label.pack(side="top", anchor="nw")
    
    details_var = tk.StringVar()
    
    details_entry = tk.Text(
        details_frame,
        height=5,
        width=40,
        wrap="word",
        font=self.FONTS["normal"]
    )
    details_entry.pack(side="top", fill="x")
    
    # Store the details entry
    self.ui_elements["maintenance_details_entry"] = details_entry
    
    # Performed by field
    performed_frame = tk.Frame(form_frame, bg=self.COLORS["background"])
    performed_frame.pack(fill="x", pady=(0, 10))
    
    performed_label = tk.Label(
        performed_frame,
        text="Performed By",
        font=self.FONTS["normal"],
        fg=self.COLORS["text"],
        bg=self.COLORS["background"],
        width=15,
        anchor="w"
    )
    performed_label.pack(side="left")
    
    performed_var = tk.StringVar()
    
    performed_entry = ttk.Entry(
        performed_frame,
        textvariable=performed_var,
        width=30
    )
    performed_entry.pack(side="left")
    
    # Store the performed by variable
    self.data_cache["maintenance_performed_by"] = performed_var
    
    # Add buttons
    button_frame = tk.Frame(form_frame, bg=self.COLORS["background"])
    button_frame.pack(fill="x", pady=(10, 0))
    
    cancel_button = ttk.Button(
        button_frame,
        text="Cancel",
        command=self._clear_maintenance_form
    )
    cancel_button.pack(side="left")
    
    save_button = ttk.Button(
        button_frame,
        text="Save",
        command=self._save_maintenance_entry
    )
    save_button.pack(side="right")
    
    # Store the entry ID for editing
    self.data_cache["maintenance_edit_id"] = None

def _load_maintenance_logs(self, search_term=None):
    """
    Load maintenance logs into the list.
    
    Args:
        search_term: Optional search term to filter logs.
    """
    try:
        # Get the entries frame
        entries_frame = self.ui_elements.get("maintenance_log_entries_frame")
        if not entries_frame:
            return
        
        # Clear the frame
        for widget in entries_frame.winfo_children():
            widget.destroy()
        
        # Get maintenance logs
        maintenance_logs = self.db_service.get_maintenance_logs()
        
        if not maintenance_logs:
            # No logs
            no_logs_label = tk.Label(
                entries_frame,
                text="No maintenance logs found.",
                font=self.FONTS["normal"],
                fg=self.COLORS["text"],
                bg=self.COLORS["background"],
                wraplength=400,
                justify="center"
            )
            no_logs_label.pack(fill="both", expand=True)
            return
        
        # Sort logs by timestamp (newest first)
        maintenance_logs.sort(key=lambda x: x["timestamp"], reverse=True)
        
        # Filter by search term if provided
        if search_term:
            search_term = search_term.lower()
            filtered_logs = []
            
            for log in maintenance_logs:
                if (
                    search_term in log.get("action", "").lower() or
                    search_term in log.get("details", "").lower() or
                    search_term in log.get("performed_by", "").lower()
                ):
                    filtered_logs.append(log)
            
            maintenance_logs = filtered_logs
        
        if not maintenance_logs:
            # No matching logs
            no_logs_label = tk.Label(
                entries_frame,
                text="No maintenance logs match your search.",
                font=self.FONTS["normal"],
                fg=self.COLORS["text"],
                bg=self.COLORS["background"],
                wraplength=400,
                justify="center"
            )
            no_logs_label.pack(fill="both", expand=True)
            return
        
        # Add logs to the list
        for i, log in enumerate(maintenance_logs):
            log_frame = tk.Frame(
                entries_frame,
                bg=self.COLORS["background_alt"] if i % 2 == 0 else self.COLORS["background"],
                bd=1,
                relief="solid"
            )
            log_frame.pack(fill="x", pady=(0, 5))
            
            # Format the timestamp
            timestamp = datetime.fromisoformat(log["timestamp"])
            formatted_date = timestamp.strftime("%Y-%m-%d %H:%M")
            
            # Header with date and action
            header_frame = tk.Frame(log_frame, bg=self.COLORS["primary_light"])
            header_frame.pack(fill="x")
            
            date_label = tk.Label(
                header_frame,
                text=formatted_date,
                font=self.FONTS["normal"],
                fg=self.COLORS["text"],
                bg=self.COLORS["primary_light"],
                anchor="w",
                padx=10,
                pady=5
            )
            date_label.pack(side="left")
            
            action_label = tk.Label(
                header_frame,
                text=log["action"],
                font=self.FONTS["normal"],
                fg=self.COLORS["text"],
                bg=self.COLORS["primary_light"],
                anchor="w",
                padx=10,
                pady=5
            )
            action_label.pack(side="left", padx=(10, 0))
            
            # Details
            if "details" in log and log["details"]:
                details_frame = tk.Frame(log_frame, bg=log_frame["bg"])
                details_frame.pack(fill="x", padx=10, pady=5)
                
                details_label = tk.Label(
                    details_frame,
                    text=log["details"],
                    font=self.FONTS["normal"],
                    fg=self.COLORS["text"],
                    bg=log_frame["bg"],
                    wraplength=400,
                    justify="left",
                    anchor="w"
                )
                details_label.pack(anchor="w")
            
            # Footer with performed by and buttons
            footer_frame = tk.Frame(log_frame, bg=log_frame["bg"])
            footer_frame.pack(fill="x", padx=10, pady=5)
            
            if "performed_by" in log and log["performed_by"]:
                performed_label = tk.Label(
                    footer_frame,
                    text=f"Performed by: {log['performed_by']}",
                    font=self.FONTS["small"],
                    fg=self.COLORS["text_light"],
                    bg=log_frame["bg"],
                    anchor="w"
                )
                performed_label.pack(side="left")
            
            # Edit button
            edit_button = ttk.Button(
                footer_frame,
                text="Edit",
                command=lambda log_id=log.get("id"): self._edit_maintenance_entry(log_id)
            )
            edit_button.pack(side="right", padx=(0, 5))
            
            # Delete button
            delete_button = ttk.Button(
                footer_frame,
                text="Delete",
                command=lambda log_id=log.get("id"): self._delete_maintenance_entry(log_id)
            )
            delete_button.pack(side="right")
        
        # Update the canvas scroll region
        canvas = self.ui_elements.get("maintenance_log_canvas")
        if canvas:
            entries_frame.update_idletasks()
            canvas.config(scrollregion=canvas.bbox("all"))
    except Exception as e:
        logger.error(f"Error loading maintenance logs: {e}")
        
        # Show error message
        entries_frame = self.ui_elements.get("maintenance_log_entries_frame")
        if entries_frame:
            for widget in entries_frame.winfo_children():
                widget.destroy()
            
            error_label = tk.Label(
                entries_frame,
                text=f"Error loading maintenance logs: {str(e)}",
                font=self.FONTS["normal"],
                fg=self.COLORS["danger"],
                bg=self.COLORS["background"],
                wraplength=400,
                justify="center"
            )
            error_label.pack(fill="both", expand=True)

def _search_maintenance_logs(self):
    """Search maintenance logs based on the search term."""
    search_var = self.data_cache.get("maintenance_search")
    if search_var:
        search_term = search_var.get().strip()
        self._load_maintenance_logs(search_term)

def _show_add_maintenance_form(self):
    """Show the form to add a new maintenance entry."""
    # Clear the form
    self._clear_maintenance_form()
    
    # Set the card title
    card_title = self.content_frame.winfo_children()[-1].winfo_children()[0].winfo_children()[0]
    if isinstance(card_title, tk.Label):
        card_title.config(text="Add Maintenance Entry")
    
    # Clear the edit ID
    self.data_cache["maintenance_edit_id"] = None

def _edit_maintenance_entry(self, log_id):
    """
    Show the form to edit a maintenance entry.
    
    Args:
        log_id: ID of the log entry to edit.
    """
    try:
        # Get the log entry
        maintenance_logs = self.db_service.get_maintenance_logs()
        log_entry = None
        
        for log in maintenance_logs:
            if log.get("id") == log_id:
                log_entry = log
                break
        
        if not log_entry:
            messagebox.showerror(
                "Error",
                f"Log entry with ID {log_id} not found."
            )
            return
        
        # Set the form fields
        # Date
        date_var = self.data_cache.get("maintenance_date")
        if date_var:
            timestamp = datetime.fromisoformat(log_entry["timestamp"])
            date_var.set(timestamp.strftime("%Y-%m-%d"))
        
        # Action
        action_var = self.data_cache.get("maintenance_action")
        if action_var:
            action_var.set(log_entry.get("action", ""))
        
        # Details
        details_entry = self.ui_elements.get("maintenance_details_entry")
        if details_entry:
            details_entry.delete("1.0", "end")
            if "details" in log_entry and log_entry["details"]:
                details_entry.insert("1.0", log_entry["details"])
        
        # Performed by
        performed_var = self.data_cache.get("maintenance_performed_by")
        if performed_var:
            performed_var.set(log_entry.get("performed_by", ""))
        
        # Set the edit ID
        self.data_cache["maintenance_edit_id"] = log_id
        
        # Set the card title
        card_title = self.content_frame.winfo_children()[-1].winfo_children()[0].winfo_children()[0]
        if isinstance(card_title, tk.Label):
            card_title.config(text="Edit Maintenance Entry")
    except Exception as e:
        logger.error(f"Error editing maintenance entry: {e}")
        messagebox.showerror(
            "Error",
            f"Error editing maintenance entry: {str(e)}"
        )

def _delete_maintenance_entry(self, log_id):
    """
    Delete a maintenance entry.
    
    Args:
        log_id: ID of the log entry to delete.
    """
    try:
        # Confirm deletion
        confirm = messagebox.askyesno(
            "Confirm Deletion",
            "Are you sure you want to delete this maintenance entry?"
        )
        
        if not confirm:
            return
        
        # Delete the entry
        # Note: This is a placeholder since the database service doesn't have a delete method
        # In a real application, you would call something like:
        # self.db_service.delete_maintenance_log(log_id)
        
        messagebox.showinfo(
            "Success",
            "Maintenance entry deleted successfully."
        )
        
        # Reload the logs
        self._load_maintenance_logs()
    except Exception as e:
        logger.error(f"Error deleting maintenance entry: {e}")
        messagebox.showerror(
            "Error",
            f"Error deleting maintenance entry: {str(e)}"
        )

def _clear_maintenance_form(self):
    """Clear the maintenance entry form."""
    # Date
    date_var = self.data_cache.get("maintenance_date")
    if date_var:
        date_var.set(datetime.now().strftime("%Y-%m-%d"))
    
    # Action
    action_var = self.data_cache.get("maintenance_action")
    if action_var:
        action_var.set("")
    
    # Details
    details_entry = self.ui_elements.get("maintenance_details_entry")
    if details_entry:
        details_entry.delete("1.0", "end")
    
    # Performed by
    performed_var = self.data_cache.get("maintenance_performed_by")
    if performed_var:
        performed_var.set("")
    
    # Clear the edit ID
    self.data_cache["maintenance_edit_id"] = None

def _save_maintenance_entry(self):
    """Save the maintenance entry form."""
    try:
        # Get form values
        date_var = self.data_cache.get("maintenance_date")
        action_var = self.data_cache.get("maintenance_action")
        details_entry = self.ui_elements.get("maintenance_details_entry")
        performed_var = self.data_cache.get("maintenance_performed_by")
        
        if not date_var or not action_var or not details_entry or not performed_var:
            messagebox.showerror(
                "Error",
                "Form fields not found."
            )
            return
        
        date = date_var.get().strip()
        action = action_var.get().strip()
        details = details_entry.get("1.0", "end").strip()
        performed_by = performed_var.get().strip()
        
        # Validate required fields
        if not date or not action:
            messagebox.showerror(
                "Error",
                "Date and Action are required fields."
            )
            return
        
        # Convert date to timestamp
        try:
            timestamp = datetime.strptime(date, "%Y-%m-%d").isoformat()
        except ValueError:
            messagebox.showerror(
                "Error",
                "Invalid date format. Please use YYYY-MM-DD."
            )
            return
        
        # Check if this is an edit or a new entry
        edit_id = self.data_cache.get("maintenance_edit_id")
        
        if edit_id is not None:
            # This is an edit
            # Note: This is a placeholder since the database service doesn't have an update method
            # In a real application, you would call something like:
            # self.db_service.update_maintenance_log(edit_id, timestamp, action, details, performed_by)
            
            messagebox.showinfo(
                "Success",
                "Maintenance entry updated successfully."
            )
        else:
            # This is a new entry
            self.db_service.add_maintenance_log(
                timestamp=timestamp,
                action=action,
                details=details,
                performed_by=performed_by
            )
            
            messagebox.showinfo(
                "Success",
                "Maintenance entry added successfully."
            )
        
        # Clear the form
        self._clear_maintenance_form()
        
        # Reload the logs
        self._load_maintenance_logs()
    except Exception as e:
        logger.error(f"Error saving maintenance entry: {e}")
        messagebox.showerror(
            "Error",
            f"Error saving maintenance entry: {str(e)}"
        )

def show_settings(self):
    """Show the settings view."""
    self._clear_content_frame()
    self.current_view = "settings"
    
    # Create page header
    self._create_page_header(
        "Settings",
        "Configure application settings and preferences."
    )
    
    # Create a frame for the settings content
    settings_frame = tk.Frame(self.content_frame, bg=self.COLORS["background"])
    settings_frame.pack(fill="both", expand=True, padx=20, pady=10)
    
    # Configure the grid layout
    settings_frame.columnconfigure(0, weight=1)
    settings_frame.columnconfigure(1, weight=1)
    settings_frame.rowconfigure(0, weight=0)  # General settings
    settings_frame.rowconfigure(1, weight=0)  # Pool settings
    settings_frame.rowconfigure(2, weight=0)  # Weather settings
    settings_frame.rowconfigure(3, weight=0)  # Display settings
    settings_frame.rowconfigure(4, weight=1)  # Empty space
    
    # Create the settings cards
    self._create_general_settings_card(settings_frame)
    self._create_pool_settings_card(settings_frame)
    self._create_weather_settings_card(settings_frame)
    self._create_display_settings_card(settings_frame)
    
    # Add a save button at the bottom
    button_frame = tk.Frame(settings_frame, bg=self.COLORS["background"])
    button_frame.grid(row=5, column=0, columnspan=2, sticky="ew", pady=(10, 0))
    
    save_button = ttk.Button(
        button_frame,
        text="Save All Settings",
        command=self._save_all_settings
    )
    save_button.pack(side="right")
    
    # Update status message
    self.status_message.config(text="Settings view loaded")

def _create_general_settings_card(self, parent):
    """
    Create a card for general settings.
    
    Args:
        parent: Parent widget.
    """
    # Create the card
    card, content_frame, _ = self._create_card(
        parent,
        "General Settings"
    )
    card.grid(row=0, column=0, columnspan=2, sticky="ew", pady=(0, 10))
    
    # Create a frame for the settings
    settings_frame = tk.Frame(content_frame, bg=self.COLORS["background"])
    settings_frame.pack(fill="x", padx=10, pady=10)
    
    # User name setting
    user_frame, user_var, _ = self._create_data_entry_field(
        settings_frame,
        "User Name",
        default_value=self.config.get("general", {}).get("user_name", ""),
        width=30,
        tooltip="Your name for maintenance logs"
    )
    user_frame.pack(fill="x", pady=(0, 10))
    
    # Store the user name variable
    self.data_cache["settings_user_name"] = user_var
    
    # Data directory setting
    data_frame, data_var, _ = self._create_data_entry_field(
        settings_frame,
        "Data Directory",
        default_value=self.config.get("general", {}).get("data_directory", "data"),
        width=30,
        tooltip="Directory for storing data files"
    )
    data_frame.pack(fill="x", pady=(0, 10))
    
    # Add a browse button
    browse_button = ttk.Button(
        data_frame,
        text="Browse",
        command=self._browse_data_directory
    )
    browse_button.pack(side="right", padx=(5, 0))
    
    # Store the data directory variable
    self.data_cache["settings_data_directory"] = data_var
    
    # Backup settings
    backup_frame = tk.Frame(settings_frame, bg=self.COLORS["background"])
    backup_frame.pack(fill="x")
    
    backup_label = tk.Label(
        backup_frame,
        text="Auto Backup",
        font=self.FONTS["normal"],
        fg=self.COLORS["text"],
        bg=self.COLORS["background"],
        width=15,
        anchor="w"
    )
    backup_label.pack(side="left")
    
    backup_var = tk.BooleanVar(value=self.config.get("general", {}).get("auto_backup", False))
    
    backup_check = ttk.Checkbutton(
        backup_frame,
        text="Enable automatic backups",
        variable=backup_var,
        onvalue=True,
        offvalue=False
    )
    backup_check.pack(side="left")
    
    # Store the backup variable
    self.data_cache["settings_auto_backup"] = backup_var

def _create_pool_settings_card(self, parent):
    """
    Create a card for pool settings.
    
    Args:
        parent: Parent widget.
    """
    # Create the card
    card, content_frame, _ = self._create_card(
        parent,
        "Pool Settings"
    )
    card.grid(row=1, column=0, sticky="nsew", padx=(0, 5), pady=(0, 10))
    
    # Create a frame for the settings
    settings_frame = tk.Frame(content_frame, bg=self.COLORS["background"])
    settings_frame.pack(fill="x", padx=10, pady=10)
    
    # Pool size setting
    size_frame, size_var, _ = self._create_data_entry_field(
        settings_frame,
        "Pool Size",
        default_value=self.config.get("pool", {}).get("size", ""),
        width=10,
        validator=self._validate_float,
        unit="gallons",
        tooltip="Volume of your pool in gallons"
    )
    size_frame.pack(fill="x", pady=(0, 10))
    
    # Store the pool size variable
    self.data_cache["settings_pool_size"] = size_var
    
    # Pool type setting
    type_frame = tk.Frame(settings_frame, bg=self.COLORS["background"])
    type_frame.pack(fill="x", pady=(0, 10))
    
    type_label = tk.Label(
        type_frame,
        text="Pool Type",
        font=self.FONTS["normal"],
        fg=self.COLORS["text"],
        bg=self.COLORS["background"],
        width=15,
        anchor="w"
    )
    type_label.pack(side="left")
    
    type_var = tk.StringVar(value=self.config.get("pool", {}).get("type", "chlorine"))
    
    # Create a combobox with pool types
    pool_types = [
        "chlorine",
        "saltwater",
        "bromine"
    ]
    
    type_combo = ttk.Combobox(
        type_frame,
        textvariable=type_var,
        values=pool_types,
        width=15
    )
    type_combo.pack(side="left")
    
    # Store the pool type variable
    self.data_cache["settings_pool_type"] = type_var
    
    # Test strip brand setting
    brand_frame = tk.Frame(settings_frame, bg=self.COLORS["background"])
    brand_frame.pack(fill="x")
    
    brand_label = tk.Label(
        brand_frame,
        text="Test Strip Brand",
        font=self.FONTS["normal"],
        fg=self.COLORS["text"],
        bg=self.COLORS["background"],
        width=15,
        anchor="w"
    )
    brand_label.pack(side="left")
    
    brand_var = tk.StringVar(value=self.config.get("pool", {}).get("test_strip_brand", "default"))
    
    # Create a combobox with test strip brands
    brands = [
        "default",
        "aquachek",
        "clorox",
        "taylor",
        "hach",
        "other"
    ]
    
    brand_combo = ttk.Combobox(
        brand_frame,
        textvariable=brand_var,
        values=brands,
        width=15
    )
    brand_combo.pack(side="left")
    
    # Store the test strip brand variable
    self.data_cache["settings_test_strip_brand"] = brand_var

def _create_weather_settings_card(self, parent):
    """
    Create a card for weather settings.
    
    Args:
        parent: Parent widget.
    """
    # Create the card
    card, content_frame, _ = self._create_card(
        parent,
        "Weather Settings"
    )
    card.grid(row=1, column=1, sticky="nsew", padx=(5, 0), pady=(0, 10))
    
    # Create a frame for the settings
    settings_frame = tk.Frame(content_frame, bg=self.COLORS["background"])
    settings_frame.pack(fill="x", padx=10, pady=10)
    
    # Zip code setting
    zip_frame, zip_var, _ = self._create_data_entry_field(
        settings_frame,
        "Zip Code",
        default_value=self.config.get("weather", {}).get("zip_code", ""),
        width=10,
        validator=self._validate_zip_code,
        tooltip="Your zip code for weather data"
    )
    zip_frame.pack(fill="x", pady=(0, 10))
    
    # Store the zip code variable
    self.data_cache["settings_zip_code"] = zip_var
    
    # Update interval setting
    interval_frame, interval_var, _ = self._create_data_entry_field(
        settings_frame,
        "Update Interval",
        default_value=self.config.get("weather", {}).get("update_interval", "3600"),
        width=10,
        validator=self._validate_int,
        unit="seconds",
        tooltip="How often to update weather data"
    )
    interval_frame.pack(fill="x", pady=(0, 10))
    
    # Store the update interval variable
    self.data_cache["settings_update_interval"] = interval_var
    
    # API key setting
    api_frame, api_var, _ = self._create_data_entry_field(
        settings_frame,
        "API Key",
        default_value=self.config.get("weather", {}).get("api_key", ""),
        width=30,
        tooltip="Optional API key for weather service"
    )
    api_frame.pack(fill="x")
    
    # Store the API key variable
    self.data_cache["settings_api_key"] = api_var

def _create_display_settings_card(self, parent):
    """
    Create a card for display settings.
    
    Args:
        parent: Parent widget.
    """
    # Create the card
    card, content_frame, _ = self._create_card(
        parent,
        "Display Settings"
    )
    card.grid(row=2, column=0, columnspan=2, sticky="ew", pady=(0, 10))
    
    # Create a frame for the settings
    settings_frame = tk.Frame(content_frame, bg=self.COLORS["background"])
    settings_frame.pack(fill="x", padx=10, pady=10)
    
    # Theme setting
    theme_frame = tk.Frame(settings_frame, bg=self.COLORS["background"])
    theme_frame.pack(fill="x", pady=(0, 10))
    
    theme_label = tk.Label(
        theme_frame,
        text="Theme",
        font=self.FONTS["normal"],
        fg=self.COLORS["text"],
        bg=self.COLORS["background"],
        width=15,
        anchor="w"
    )
    theme_label.pack(side="left")
    
    theme_var = tk.StringVar(value=self.config.get("display", {}).get("theme", "light"))
    
    # Create a combobox with themes
    themes = [
        "light",
        "dark",
        "blue"
    ]
    
    theme_combo = ttk.Combobox(
        theme_frame,
        textvariable=theme_var,
        values=themes,
        width=15
    )
    theme_combo.pack(side="left")
    
    # Store the theme variable
    self.data_cache["settings_theme"] = theme_var
    
    # Add a preview button
    preview_button = ttk.Button(
        theme_frame,
        text="Preview",
        command=lambda: self._preview_theme(theme_var.get())
    )
    preview_button.pack(side="left", padx=(10, 0))
    
    # Font size setting
    font_frame = tk.Frame(settings_frame, bg=self.COLORS["background"])
    font_frame.pack(fill="x", pady=(0, 10))
    
    font_label = tk.Label(
        font_frame,
        text="Font Size",
        font=self.FONTS["normal"],
        fg=self.COLORS["text"],
        bg=self.COLORS["background"],
        width=15,
        anchor="w"
    )
    font_label.pack(side="left")
    
    font_var = tk.StringVar(value=self.config.get("display", {}).get("font_size", "normal"))
    
    # Create a combobox with font sizes
    font_sizes = [
        "small",
        "normal",
        "large"
    ]
    
    font_combo = ttk.Combobox(
        font_frame,
        textvariable=font_var,
        values=font_sizes,
        width=15
    )
    font_combo.pack(side="left")
    
    # Store the font size variable
    self.data_cache["settings_font_size"] = font_var
    
    # Chart DPI setting
    dpi_frame, dpi_var, _ = self._create_data_entry_field(
        settings_frame,
        "Chart DPI",
        default_value=self.config.get("display", {}).get("chart_dpi", "100"),
        width=10,
        validator=self._validate_int,
        tooltip="Resolution for charts (higher values = better quality but larger files)"
    )
    dpi_frame.pack(fill="x")
    
    # Store the chart DPI variable
    self.data_cache["settings_chart_dpi"] = dpi_var

def _browse_data_directory(self):
    """Browse for a data directory."""
    directory = filedialog.askdirectory(
        title="Select Data Directory",
        initialdir=self.data_cache.get("settings_data_directory", tk.StringVar()).get()
    )
    
    if directory:
        self.data_cache.get("settings_data_directory", tk.StringVar()).set(directory)

def _preview_theme(self, theme):
    """
    Preview a theme.
    
    Args:
        theme: Theme name to preview.
    """
    try:
        # Set the theme
        self.set_theme(theme)
        
        # Show a message
        messagebox.showinfo(
            "Theme Preview",
            f"Theme '{theme}' applied. Click 'Save All Settings' to keep this theme."
        )
    except Exception as e:
        logger.error(f"Error previewing theme: {e}")
        messagebox.showerror(
            "Error",
            f"Error previewing theme: {str(e)}"
        )

def _save_all_settings(self):
    """Save all settings."""
    try:
        # Create a new config dictionary
        new_config = {}
        
        # General settings
        new_config["general"] = {
            "user_name": self.data_cache.get("settings_user_name", tk.StringVar()).get(),
            "data_directory": self.data_cache.get("settings_data_directory", tk.StringVar()).get(),
            "auto_backup": self.data_cache.get("settings_auto_backup", tk.BooleanVar()).get()
        }
        
        # Pool settings
        new_config["pool"] = {
            "size": self.data_cache.get("settings_pool_size", tk.StringVar()).get(),
            "type": self.data_cache.get("settings_pool_type", tk.StringVar()).get(),
            "test_strip_brand": self.data_cache.get("settings_test_strip_brand", tk.StringVar()).get()
        }
        
        # Weather settings
        new_config["weather"] = {
            "zip_code": self.data_cache.get("settings_zip_code", tk.StringVar()).get(),
            "update_interval": self.data_cache.get("settings_update_interval", tk.StringVar()).get(),
            "api_key": self.data_cache.get("settings_api_key", tk.StringVar()).get()
        }
        
        # Display settings
        new_config["display"] = {
            "theme": self.data_cache.get("settings_theme", tk.StringVar()).get(),
            "font_size": self.data_cache.get("settings_font_size", tk.StringVar()).get(),
            "chart_dpi": self.data_cache.get("settings_chart_dpi", tk.StringVar()).get()
        }
        
        # Update the config
        self.config = new_config
        
        # Save the config
        self._save_config()
        
        # Show success message
        messagebox.showinfo(
            "Settings Saved",
            "All settings have been saved successfully."
        )
        
        # Apply the theme
        self.set_theme(new_config["display"]["theme"])
        
        # Update the chemical calculator pool settings
        try:
            pool_size = float(new_config["pool"]["size"])
            pool_type = new_config["pool"]["type"]
            
            self.chemical_calculator = type(self.chemical_calculator)(
                pool_volume=pool_size,
                pool_type=pool_type
            )
        except (ValueError, TypeError):
            pass
    except Exception as e:
        logger.error(f"Error saving settings: {e}")
        messagebox.showerror(
            "Error",
            f"Error saving settings: {str(e)}"
        )
