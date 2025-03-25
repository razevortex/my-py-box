import qrcode
from PIL import Image


class QRC(qrcode.QRCode):
	def __init__(self, version=1,
	             error_correction=qrcode.constants.ERROR_CORRECT_L,
	             box_size=10, border=4,
	             data=''
	             ):
		super().__init__(version=version, error_correction=error_correction, box_size=box_size, border=border)
		self.add_data(data)
		self.make(fit=True)
	
	def export_img(self, fname='qrcode.png'):
		self.make_image(fill_color="black", back_color='white').save(fname)

if __name__ == '__main__':
	QRC(data="hello world").export_img()
