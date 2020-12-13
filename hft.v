module hft(

input clk,
input rx,
output tx,
output [9:0] debug
	);


wire [7:0] addr;
wire [31:0] rx_buyprice;
wire [31:0] rx_sellprice;
wire [31:0] rx_buyvol;
wire [31:0] rx_sellvol;
wire rx_dv;

wire [7:0] tx_addr; 
wire [7:0] tx_buysell;
wire [31:0] tx_timestamp;
wire tx_dv;
wire tx_busy;

wire [7:0] addr0; 
wire [31:0] rx_buyprice0;
wire [31:0] rx_sellprice0;
wire [31:0] rx_buyvol0;
wire [31:0] rx_sellvol0;
wire rx_dv0;

wire [7:0] tx_addr0; 
wire [7:0] tx_buysell0;
wire [31:0] tx_timestamp0;
wire tx_dv0;

reg reset_n;
always@(posedge clk)
begin
	reset_n <= 1;
end

//instantiate the UART modules
uart uu0(
.clk (clk),
.reset_n (reset_n),

.rx (rx), //physical line
.tx (tx),

.algo_addr (addr), //to rx mux
.algo_buyprice (rx_buyprice),
.algo_sellprice (rx_sellprice),
.algo_buyvol (rx_buyvol),
.algo_sellvol (rx_sellvol),
.rx_dv (rx_dv),

.tx_addr (tx_addr), //from tx mux
.tx_buysell (tx_buysell),
.tx_timestamp (tx_timestamp),
.tx_dv (tx_dv),
.tx_busy (tx_busy),

.debug(debug)

	);

//instantiate the RX addr mux
rx_mux rum0(
.clk (clk),
.reset_n (reset_n),

.addr (addr), //from uart
.rx_buyprice (rx_buyprice),
.rx_sellprice (rx_sellprice),
.rx_buyvol (rx_buyvol),
.rx_sellvol (rx_sellvol),
.rx_dv (rx_dv),

.addr0 (addr0), //to system0
.rx_buyprice0 (rx_buyprice0),
.rx_sellprice0 (rx_sellprice0),
.rx_buyvol0 (rx_buyvol0),
.rx_sellvol0 (rx_sellvol0),
.rx_dv0 (rx_dv0)
	);

//instantiate the TX addr mux
tx_mux tux0(
.clk (clk),
.reset_n (reset_n),

.tx_addr0 (tx_addr0), //from system0
.tx_buysell0 (tx_buysell0),
.tx_timestamp0 (tx_timestamp0),
.tx_dv0 (tx_dv0),


.tx_addr (tx_addr), //to uart
.tx_buysell (tx_buysell),
.tx_timestamp (tx_timestamp),
.tx_dv (tx_dv),
.tx_busy (tx_busy)
	);

//instantiate the system addr 0
system sys0(
.clk (clk),
.reset_n (reset_n),

.addr0 (addr0), //from rx_mux
.rx_buyprice0 (rx_buyprice0),
.rx_sellprice0 (rx_sellprice0),
.rx_buyvol0 (rx_buyvol0),
.rx_sellvol0 (rx_sellvol0),
.rx_dv0 (rx_dv0),


.tx_addr0 (tx_addr0), //to tx_mux
.tx_buysell0 (tx_buysell0),
.tx_timestamp0 (tx_timestamp0),
.tx_dv0 (tx_dv0)
	);



endmodule

