while text_size.width() > screen_size.width() - 10 or text_size.height() > screen_size.height() - 10:
	font_size -= 1
	nf = QFont("Arial", font_size)
	nf.setBold(True)
	self.screens[s].label.setFont(nf)
	if config.get(f"screen_{s}", "show_words") == "1":
		self.screens[s].label.setText(active_text.strip())
	if config.get(f"screen_{s}", "stream_mode") == "0":
		self.screens[s].label.setWordWrap(True)
	self.screens[s].label.adjustSize()
	screen_size = QDesktopWidget().availableGeometry(s)
	text_size = self.screens[s].label.size()

	screen_center_x = screen_size.width() / 2
	screen_center_y = screen_size.height() / 2
	text_center_x = text_size.width() / 2
	text_center_y = text_size.height() / 2

	if config.get(f"screen_{s}", "stream_mode") == "0":
		self.screens[s].label.move(screen_center_x - text_center_x, screen_center_y - text_center_y)
			
	if config.get(f"screen_{s}", "stream_mode") == "1":
		self.screens[s].label.move(screen_center_x - text_center_x, screen_size.height() - int(config.get(f"screen_{s}", "margin_bottom")))

	self.screens[s].label.setScaledContents(True)