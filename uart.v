module uart(

input clk,
input reset_n,
input rx,
output tx

output reg [7:0] addr;
output reg [31:0] rx_buyprice;
output reg [31:0] rx_sellprice;
output reg [31:0] rx_buyvol;
output reg [31:0] rx_sellvol;
output reg rx_dv;

input [7:0] tx_addr;
input [31:0] tx_buyprice;
input [31:0] tx_sellprice;
input [31:0] tx_buyvol;
input [31:0] tx_sellvol;
input tx_dv;
);

/*
byte structure: (START, ADDR, BUYPRICE MSB3, 2, 1, 0, SELLPRICE MSB3, 2, 1, 0, BUYVOL MSB3, 2, 1, 0
                 ,SELLVOL MSB3, 2, 1, 0, STOP)
START = 8'b 11110000
STOP = 8'd' 00001111
total bytes per transaction: 19
*/



//RX State machine:  pull frame in from UART, pass to top module/mux
wire uart_rx_dv;
wire [7:0] uart_rx_data;
reg [3:0] rx_state;
reg [7:0] rx_start;
reg [7:0] rx_addr;
reg [31:0] rx_buyprice;
reg [31:0] rx_sellprice;
reg [31:0] rx_buyvol;
reg [31:0] rx_sellvol;
reg [7:0] rx_stop;

always@(posedge clk)
begin
	case rx_state:
	0:
	begin
	rx_dv <= 0;
		if(uart_rx_dv) 
			begin
			rx_start <= uart_rx_data;
			rx_state <= 1;
			end
		else rx_state <= 0;
	end
	1:
	begin
		if(rx_start == 8'b11110000) //start delimiter is valid, proceed to read the message in
			begin
			rx_state <= 2;
			end
		else rx_state <= 0 //start delimiter is bad, start the scan over
	end
	2:
	begin
		if(uart_rx_dv)
			begin
			rx_addr <= uart_rx_data;
			rx_state <= 3;
			end
		else rx_state <= 2;
	end
	3://begin the buyprice receive
	begin
		if(uart_rx_dv) 
			begin
			rx_buyprice[31:24] <= uart_rx_data;
			rx_state <= 4;
			end
		else rx_state <=3;
	end
	4:
		begin
			if(uart_rx_dv)
				begin
				rx_buyprice[23:16] <= uart_rx_data;
				rx_state <= 5;
				end
			else rx_state <= 4;
		end
	5:
		begin
			if(uart_rx_dv)
				begin
				rx_buyprice[15:8] <= uart_rx_data;
				rx_state <= 6;
				end
			else rx_state <= 5;
		end
	6:
		begin
			if(uart_rx_dv)
				begin
				rx_buyprice[7:0] <= uart_rx_data;
				rx_state <= 7;
				end
			else rx_state <= 6;
		end
	7: //begin the sellprice receive
		begin
			if(uart_rx_dv)
			begin
				rx_sellprice[31:25] <= uart_rx_data;
				rx_state <= 8;
			end
			else rx_state <= 7;
		end
	8:
		begin
			if(uart_rx_dv)
			begin
				rx_sellprice[24:16] <= uart_rx_data;
				rx_state <= 9;
			end
			else rx_state <= 8;
		end
	9:
		begin
			if(uart_rx_dv)
			begin
				rx_sellprice[15:8] <= uart_rx_data;
				rx_state <= 10;
			end
			else rx_state <= 9;
		end
	10:
		begin
			if(uart_rx_dv)
			begin
				rx_sellprice[7:0] <= uart_rx_data;
				rx_state <= 11;
			end
			else rx_state <= 11;
		end
	11: //begin the buyvol receive
		begin
			if(uart_rx_dv)
			begin
				rx_buyvol[31:24] <= uart_rx_data;
				rx_state <= 12;
			end
			else rx_state <= 11;
		end
	12:
		begin
			if(uart_rx_dv)
			begin
				rx_buyvol[23:16] <= uart_rx_data;
				rx_state <=13;
			end
			else rx_state <= 12;
		end
	13:
		begin
			if(uart_rx_dv)
			begin
				rx_buyvol[15:8] <= uart_rx_data;
				rx_state <= 14;
			end
			else rx_state <= 13;
		end
	14:
		begin
			if(uart_rx_dv)
			begin
				rx_buyvol[7:0] <= uart_rx_data;
				rx_state <= 15;
			end
			else rx_state <= 14;
		end
	15://begin sellvol receive
		begin
			if(uart_rx_dv)
			begin
				rx_sellvol[31:24] <= uart_rx_data;
				rx_state <= 16;
			end
			else rx_state <= 15;
		end
	16:
		begin
			if(uart_rx_dv)
			begin
				rx_sellvol[23:16] <= uart_rx_data;
				rx_state <= 17;
			end
			else rx_state <= 16;
		end
	17:
		begin
			if(uart_rx_dv)
			begin
				rx_sellvol[15:8] <= uart_rx_data;
				rx_state <= 18;
			end
			else rx_state <= 17;
		end
	18:
		begin
			if(uart_rx_dv)
			begin
				rx_sellvol[7:0] <= uart_rx_data;
				rx_state <= 19;
			end
			else rx_state <= 18;
		end
	19: //pull in the stop byte for verification
	begin
		if(uart_rx_dv)
		begin
			rx_stop <= uart_rx_data;
			rx_state <= 20;
		end
		else rx_state <= 19;
	end
	20:
	begin
		if(rx_stop == 8'b00001111) //stop byte is good, ship it to mux
		begin
			addr <= rx_addr;
			buyprice <= rx_buyprice;
			sellprice <= rx_sellprice;
			buyvol <= rx_buyvol;
			sellvol <= rx_sellvol;
			rx_dv <= 1;
			rx_state <= 0;
		end
		else //stop byte is no good, throw out the data and start over
		begin
			addr <= 0;
			buyprice <= 0;
			sellprice <= 0;
			buyvol <= 0;
			sellvol <= 0;
			rx_dv <= 0;
			rx_state <= 0;
		end
	end
	endcase
end

//TX state machine: pull frames in from MUX, ship to UART
reg uart_tx_dv;
reg //left off here

uart_rx urx0(
.i_Clock (clk),
.i_Rx_Serial (rx),
.o_Rx_DV (uart_rx_dv),
.o_Rx_Byte (uart_rx_data),
.reset_n (reset_n)
  );

uart_tx utx0(
.i_Clock (clk),
.i_Tx_DV (uart_tx_dv),
.i_Tx_Byte (uart_tx_data),
.o_Tx_Active (uart_tx_busy),
.o_Tx_Serial (tx),
.o_Tx_Done (uart_tx_done),
.reset_n (reset_n)
  );

endmodule