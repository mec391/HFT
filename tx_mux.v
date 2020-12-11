module tx_mux(
input clk,
input reset_n,

input [7:0] tx_addr0,
input [7:0] tx_buysell0,
input [31:0] tx_timestamp0,
input tx_dv0,

output reg [7:0] tx_addr,
output reg [7:0] tx_buysell,
output reg [31:0] tx_timestamp,
output reg tx_dv,
input tx_busy
);

//for now just run straight into uart
always@(posedge clk)
begin
	if(tx_dv0)
	begin
	tx_addr <= tx_addr0;
	tx_buysell <= tx_buysell0;
	tx_timestamp <= tx_timestamp0;
	tx_dv <= 1;
	end
	else begin
	tx_addr <= 0;
	tx_buysell <= 0;
	tx_timestamp <= 0;
	tx_dv <= 0;
	end
end

endmodule

//below is starting code for a fifo that takes in multiple systems and outputs a single value to the fifo
//will need multiple fifos/rams that the tx_mux cycles through to work (i need to rewrite it)
/*
reg [6:0] input_pointer;
reg [6:0] output_pointer;
reg [6:0] counter;
reg [3:0] SM_in;
reg [3:0] SM_out;

//ram0:
//0: addr
//1: buysell
//2: timestamp


//instantiate a dual port ram that acts as a circular buffer, write to the circular buffer from system0-n
//read from circular buffer from the tx_mux and write to uart when possible 

//if tx_dv0, write the data into the buffer at the input pointer, move the pointer up, add 1 to counter
//if counter < 0, read the data from the buffer at the output pointer, move the pointer up, remove 1 from counter
always@(posedge clk)
begin
		case SM_in:
		0:
		begin
		if(tx_dv0)
			addr_a <= input_pointer;
			we_a <= 1;
			data_a <= tx_addr0;
		end
		
		endcase
		end
	

	if(counter > 0) 
		begin
		case SM_out:
		0:
		begin
			tx_dv <= 0;

		end
		endcase



.TD_DPRAM dp0(
.clk (clk)
.data_a (data_a);
.data_b (data_b);

.addr_a (addr_a);
.addr_b (addr_b);
.we_a (we_a);
.we_b (we_b);
.q_a (q_a);
.q_b (q_b);
	);


endmodule



module TD_DPRAM
(


	input [31:0] data_a, data_b, //24 bit data inputs
	input [6:0] addr_a, addr_b, //3 BIT ADDRESSES 0-6
	input we_a, we_b, clk, //write enables and clk
	output reg [31:0] q_a, q_b //24 bit data output
);

	// Declare the RAM variable
	reg [31:0] ram[99:0]; //24 bit data 7 addresses,
						//addr sel takes reg 42-48 and sends
						//0-6..
						//2 unused regs, 8:0 is min for inference
	
	// Port A
	always @ (posedge clk)
	begin
		if (we_a) 
		begin
			ram[addr_a] <= data_a;
			q_a <= data_a;
		end
		else 
		begin
			q_a <= ram[addr_a];
		end
	end
	
	// Port B
	always @ (posedge clk)
	begin
		if (we_b)
		begin
			ram[addr_b] <= data_b;
			q_b <= data_b;
		end
		else
		begin
			q_b <= ram[addr_b];
		end
	end
	
endmodule
*/