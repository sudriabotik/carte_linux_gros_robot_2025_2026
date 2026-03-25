import gpiod
import datetime



class GpioWrapper :

	def __init__(self) :

		chip = gpiod.Chip("/dev/gpiochip4")

		self.request = gpiod.request_lines(
			"/dev/gpiochip4",
			consumer="async-watch-line-value",
			config={
				(6) : gpiod.LineSettings(
					edge_detection = gpiod.line.Edge.BOTH,
					debounce_period = datetime.timedelta(milliseconds=10),
				)
			}
		)





	def test(self) :

		while True:
			for event in self.request.read_edge_events():
				print(
					"offset: {}  type: {:<7}  event #{}  line event #{}".format(
						event.line_offset,
						str(event),
						event.global_seqno,
						event.line_seqno,
					)
				)



