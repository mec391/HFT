module uart(

input clk,
input reset_n,
input rx,
output tx,

//to rx_mux:
output reg [7:0] algo_addr, 
output reg [31:0] algo_buyprice,
output reg [31:0] algo_sellprice,
output reg [31:0] algo_buyvol,
output reg [31:0] algo_sellvol,
output reg rx_dv,

//from tx_mux:
input [7:0] tx_addr,
input [7:0] tx_buysell,
input [31:0] tx_timestamp,
input tx_dv,
output reg tx_busy,

output reg [9:0] debug
);
//Least significant byte is sent out first
/*
byte structure ON RX: (START, ADDR, BUYPRICE LSB0, 1, 2, 3MSB, SELLPRICE LSB0, 1, 2, 3, BUYVOL LSB0, 1, 2, 3
                 ,SELLVOL LSB0, 1, 2, 3, STOP)
START = 8'b 11110000
STOP = 8'b' 00001111
total bytes per transaction: 19
*/

/*
byte structure on TX: (START, ADDR, BUY/SELL, 4BYTE TIMESTAMP LSB0, 1, 2 ,3, STOP)
START = 8'b 10000000
STOP = 8'b' 00000001
assume that the buy/sell decision will be sent back to python before python increments to the next update
this makes it so I do not need to send back the buy/sell price and volume 
*/

//RX State machine:  pull frame in from UART, pass to top module/mux
wire uart_rx_dv;
wire [7:0] uart_rx_data;
reg [4:0] rx_state;
reg [7:0] rx_start;
reg [7:0] rx_addr;
reg [31:0] rx_buyprice;
reg [31:0] rx_sellprice;
reg [31:0] rx_buyvol;
reg [31:0] rx_sellvol;
reg [7:0] rx_stop;

wire half_clk;
reg [5:0] ds;
//debug state machine:
always@(posedge half_clk)
begin
	debug[7:0] <= rx_buyprice[31:24];
	/*case (ds)
		0:
	if(rx_buyprice != 0)begin
		debug[7:0] <= rx_buyprice[31:24];
		ds <= 1;
	end
	1:
	begin
	 if (rx_sellprice != 0) 
	 	begin
	 		debug[7:0] <= rx_sellprice[31:24];
			ds <= 2;
		end
		end
		2:
		begin
	if (rx_buyvol != 0) begin
		debug[7:0] <= rx_buyvol[31:24];
		ds <=3;
	end
	end
	3:begin
	if (rx_sellvol != 0) begin
		debug[7:0] <= rx_buyvol[31:24];
		ds <= 3;
	end
	end
	//if (rx_state == 20) debug <= debug + 1;
endcase
*/
end
always@(posedge half_clk)
begin
	case (rx_state)
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
		if(rx_start == 8'd240) //start delimiter is valid, proceed to read the message in
			begin
			rx_state <= 2;
			rx_start <= 0;
			end
		else 
		begin
		rx_state <= 0; //start delimiter is bad, start the scan over
		rx_start <=0;
		end 
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
	3://begin the buyprice left receive
	begin
		if(uart_rx_dv) 
			begin
			rx_buyprice[23:16] <= uart_rx_data;
			rx_state <= 4;
			end
		else rx_state <=3;
	end
	4:
		begin
			if(uart_rx_dv)
				begin
				rx_buyprice[31:24] <= uart_rx_data;
				rx_state <= 5;
				end
			else rx_state <= 4;
		end
	5:
		begin //buyprice right
			if(uart_rx_dv)
				begin
				rx_buyprice[7:0] <= uart_rx_data;
				rx_state <= 6;
				end
			else rx_state <= 5;
		end
	6:
		begin
			if(uart_rx_dv)
				begin
				rx_buyprice[15:8] <= uart_rx_data;
				rx_state <= 7;
				end
			else rx_state <= 6;
		end
	7: //begin the sellprice left receive
		begin
			if(uart_rx_dv)
			begin
				rx_sellprice[23:16] <= uart_rx_data;
				rx_state <= 8;
			end
			else rx_state <= 7;
		end
	8:
		begin
			if(uart_rx_dv)
			begin
				rx_sellprice[31:24] <= uart_rx_data;
				rx_state <= 9;
			end
			else rx_state <= 8;
		end
	9:
		begin
			if(uart_rx_dv)//sellprice right
			begin
				rx_sellprice[7:0] <= uart_rx_data;
				rx_state <= 10;
			end
			else rx_state <= 9;
		end
	10:
		begin
			if(uart_rx_dv)
			begin
				rx_sellprice[15:8] <= uart_rx_data;
				rx_state <= 11;
			end
			else rx_state <= 11;
		end
	11: //begin the buyvol left receive
		begin
			if(uart_rx_dv)
			begin
				rx_buyvol[23:16] <= uart_rx_data;
				rx_state <= 12;
			end
			else rx_state <= 11;
		end
	12:
		begin
			if(uart_rx_dv)
			begin
				rx_buyvol[31:24] <= uart_rx_data;
				rx_state <=13;
			end
			else rx_state <= 12;
		end
	13:
		begin//buyvol right
			if(uart_rx_dv)
			begin
				rx_buyvol[7:0] <= uart_rx_data;
				rx_state <= 14;
			end
			else rx_state <= 13;
		end
	14:
		begin
			if(uart_rx_dv)
			begin
				rx_buyvol[15:8] <= uart_rx_data;
				rx_state <= 15;
			end
			else rx_state <= 14;
		end
	15://begin sellvol left receive
		begin
			if(uart_rx_dv)
			begin
				rx_sellvol[23:16] <= uart_rx_data;
				rx_state <= 16;
			end
			else rx_state <= 15;
		end
	16:
		begin
			if(uart_rx_dv)
			begin
				rx_sellvol[31:24] <= uart_rx_data;
				rx_state <= 17;
			end
			else rx_state <= 16;
		end
	17:
		begin//sellvol right
			if(uart_rx_dv)
			begin
				rx_sellvol[7:0] <= uart_rx_data;
				rx_state <= 18;
			end
			else rx_state <= 17;
		end
	18:
		begin
			if(uart_rx_dv)
			begin
				rx_sellvol[15:8] <= uart_rx_data;
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
		if(rx_stop == 8'd15) //stop byte is good, ship it to mux
		begin
			algo_addr <= rx_addr;
			algo_buyprice <= rx_buyprice;
			algo_sellprice <= rx_sellprice;
			algo_buyvol <= rx_buyvol;
			algo_sellvol <= rx_sellvol;
			rx_dv <= 1;
			rx_state <= 0;
			rx_stop <=0;
		end
		else //stop byte is no good, throw out the data and start over
		begin
			algo_addr <= 0;
			algo_buyprice <= 0;
			algo_sellprice <= 0;
			algo_buyvol <= 0;
			algo_sellvol <= 0;
			rx_dv <= 0;
			rx_state <= 0;
			rx_stop <= 0;
		end
	end
	endcase
end

//TX state machine: pull frames in from MUX, ship to UART
reg uart_tx_dv;
reg [7:0] uart_tx_data;
wire uart_tx_busy;
wire uart_tx_done;
reg [7:0] uart_tx_addr;
reg [7:0] uart_tx_buysell;
reg [31:0] uart_tx_timestamp;
reg [5:0] tx_state;
reg [7:0] uart_tx_start = 8'b10000000;
reg [7:0] uart_tx_stop =  8'b00000001;

always@(posedge half_clk)
begin
	case (tx_state)
	0:
	begin
	uart_tx_dv <= 0;
		if(tx_dv) //mux has data for me, reg it, set the tx_busy line high
		begin
		uart_tx_addr <= tx_addr;
		uart_tx_buysell <= tx_buysell;
		uart_tx_timestamp <= tx_timestamp;
		tx_state <= 1;
		tx_busy <= 1;
		end
		else tx_state <= 0;
	end
	1: //send the start byte
	begin
		if(!uart_tx_busy)
		begin
			uart_tx_data <= uart_tx_start;
			uart_tx_dv <= 1;
			tx_state <= 2;
		end
		else tx_state <= 1;
	end
	2: //send the addr
	begin
		if(!uart_tx_busy)
		begin
			uart_tx_data <= uart_tx_addr;
			uart_tx_dv <= 1;
			tx_state <= 3;
		end
		else begin
		tx_state <= 2;
		uart_tx_dv <= 0;
		end
	end
	3: //send the buysell signal
	begin
		if(!uart_tx_busy)
		begin
			uart_tx_data <= uart_tx_buysell;
			uart_tx_dv <= 1;
			tx_state <= 4;
		end
		else begin
		tx_state <= 3;
		uart_tx_dv <= 0;
		end
	end
	4://send the timestamp
	begin
		if(!uart_tx_busy)
		begin
			uart_tx_data <= uart_tx_timestamp[7:0];
			uart_tx_dv <= 1;
			tx_state <= 5;
		end
		else begin
		tx_state <= 4;
		uart_tx_dv <= 0;
		end
	end
	5:
	begin
		if(!uart_tx_busy)
		begin
			uart_tx_data <= uart_tx_timestamp[15:8];
			uart_tx_dv <= 1;
			tx_state <= 6;
		end
		else begin
		tx_state <= 5;
		uart_tx_dv <= 0;
		end
	end
	6:
	begin
		if(!uart_tx_busy)
		begin
			uart_tx_data <= uart_tx_timestamp[24:16];
			uart_tx_dv <= 1;
			tx_state <= 7;
		end
		else begin
		tx_state <= 6;
		uart_tx_dv <= 0;
		end
	end
	7:
	begin
		if(!uart_tx_busy)
		begin
			uart_tx_data <= uart_tx_timestamp[31:25];
			uart_tx_dv <= 1;
			tx_state <= 8;
		end
		else begin
		tx_state <= 7;
		uart_tx_dv <= 0;
		end
	end
	8: //send the stop byte, turn off tx_busy
	begin
		if(!uart_tx_busy)
		begin
			uart_tx_data <= uart_tx_stop;
			uart_tx_dv <= 1;
			tx_state <= 0;
			tx_busy <= 0;
		end
		else begin
		tx_state <= 8;
		uart_tx_dv <= 0;
		end
	end
	endcase
end



divide_by_2 dv2(
.clk (clk),
.reset_n (reset_n),
.half_clk(half_clk)

);


UART_RX urx0(
.i_Rst_L (reset_n),
.i_Clock (half_clk),
.i_RX_Serial (rx),
.o_RX_DV (uart_rx_dv),
.o_RX_Byte (uart_rx_data)
  );

UART_TX utx0(
.i_Rst_L (reset_n),
.i_Clock (half_clk),
.i_TX_DV (uart_tx_dv),
.i_TX_Byte (uart_tx_data), 
.o_TX_Active (uart_tx_busy),
.o_TX_Serial (tx),
.o_TX_Done (uart_tx_done)
  );

endmodule



module divide_by_2 
(
input clk,
input reset_n,
output reg half_clk
  );


 always@(posedge clk)
  begin
      if(~reset_n)
        begin
          half_clk <= 0;
        end
      else begin
        half_clk <= ~half_clk;
      end
  end

 endmodule