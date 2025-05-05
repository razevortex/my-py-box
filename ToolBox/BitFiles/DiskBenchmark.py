from ToolBox.BitFile import BitFile
from ToolBox.ProgressDisplay import ProgressConsole
from time import perf_counter_ns as nsec
from pathlib import Path


class Block(BitFile):
	@classmethod
	def ByteSize(cls, value:int, unit:str='b'):
		length = None
		value = BitFile.i2b(value, _N=10)
		for i, u in enumerate(('b', 'k', 'm', 'g')):
			if unit.casefold().startswith(u):
				length = value + BitFile.i2b(0, _N=(i * 10) + 3)
		assert length is not None, 'unit needs to be a string value starting with b, k, m or g'
		size = length.b2i(None)
		string = '1' * size
		return cls(string)
		

class DriveBenchmark:
	def __init__(self, drive, block, n_blocks, runs):
		self.benchmark_file = Path(drive, 'bench.bin')
		self.time_results = {'write': [], 'read': []}
		self.progress = ProgressConsole(runs * 2)
		self.block = block
		self.bytes_in_block = len(self.block) // 8
		self.n_blocks = n_blocks
		self.runs = runs
	
	def verify(self, obj=None):
		if obj is None:
			return len(self.block) * self.n_blocks == self.benchmark_file.stat().st_size * 8
		else:
			obj = len(obj) // 2 * 16
			return len(self.block) * self.n_blocks == obj
		
	def setup(self):
		with open(self.benchmark_file, 'bw') as f:
			f.write(b'')
			
	def cleanup(self):
		if self.benchmark_file.exists():
			self.benchmark_file.unlink()
	
	def write(self):
		with open(self.benchmark_file, 'ab') as f:
			for _ in range(self.n_blocks):
				self.block.tofile(f)
		return None
	
	def read(self):
		with open(self.benchmark_file, 'rb') as f:
			byte = f.read(self.bytes_in_block)
			for i in range(self.n_blocks):
				byte += f.read(self.bytes_in_block)
		return byte
	
	@staticmethod
	def performance(block, time):
		mb = len(block) / 1024 / 1024 / 8
		sec = time * 10 ** -9
		temp = f'{mb/sec}'
		return f'{temp[:temp.index(".")+4]}MB/s'
	
	def single_pass(self):
		for op in ('write', 'read'):
			self.progress.step()
			start = nsec()
			t = self.__getattribute__(op)()
			self.time_results[op].append(nsec()-start)
			assert self.verify(t), 'Some Error that lead to some unexcpected filesize'
		self.cleanup()

	def show_results(self):
		print(f'avg of {self.runs} runs:')
		print(f'write: {self.performance(self.block, sum(self.time_results["write"]) / len(self.time_results["write"]))}\n'
		      f'read: {self.performance(self.block, sum(self.time_results["read"]) / len(self.time_results["read"]))}')
		
	def run(self):
		for run in range(self.runs):
			self.single_pass()
		self.progress.step()
		self.show_results()
		

if __name__ == '__main__':
	block = Block.ByteSize(256, 'm')
	bench = DriveBenchmark('C:', block, 4, 5)
	bench.run()
