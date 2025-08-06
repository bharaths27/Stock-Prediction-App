import { useState, useEffect } from "react";
import axios from "axios";
import { Search, TrendingUp, ChevronsUpDown } from "lucide-react";
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer,
  ReferenceLine,
  CartesianGrid,
} from "recharts";

// Shadcn/UI Components
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";

// A custom component for displaying key-value stats
const Stat = ({ label, value }) => (
  <div className="flex justify-between text-sm">
    <p className="text-muted-foreground">{label}</p>
    <p className="font-medium text-foreground">{value || "N/A"}</p>
  </div>
);

// Helper function to format chart date labels
const formatDate = (dateStr, timeframe) => {
  const date = new Date(dateStr);
  if (isNaN(date.getTime())) return dateStr;

  switch (timeframe) {
    case '1D':
      return date.toLocaleTimeString('en-US', { hour: 'numeric', minute: '2-digit' });
    case '1W':
      return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric' });
    case '1M':
      return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric' });
    default:
      return date.toLocaleDateString('en-US', { month: 'short', year: 'numeric' });
  }
};

export default function Home() {
  // State variables
  const [company, setCompany] = useState("");
  const [suggestions, setSuggestions] = useState([]);
  const [selectedCompany, setSelectedCompany] = useState(null);
  const [companyList, setCompanyList] = useState([]);
  const [stockHistory, setStockHistory] = useState([]);
  const [timeframe, setTimeframe] = useState("1Y");
  const [stockMetrics, setStockMetrics] = useState(null);
  const [predictedTimeframe, setPredictedTimeframe] = useState("1W");
  const [predictedData, setPredictedData] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  const [isPredicting, setIsPredicting] = useState(false);
  const [showAllCompaniesOpen, setShowAllCompaniesOpen] = useState(false);
  const [modelType, setModelType] = useState('linear'); // State for model selection
  
  const currentPrice = stockHistory[stockHistory.length - 1]?.close;

  // --- Data Fetching ---
  useEffect(() => {
    const fetchAllCompanies = async () => {
      try {
        const response = await axios.get("${process.env.NEXT_PUBLIC_API_URL}/all_companies");
        setCompanyList(response.data || []);
      } catch (error) {
        console.error("Error fetching company list", error);
      }
    };
    fetchAllCompanies();
  }, []);

  const handleSearch = async (query = company) => {
    if (!query.trim()) return;
    setIsLoading(true);
    setSuggestions([]);

    try {
      const response = await axios.get(`${process.env.NEXT_PUBLIC_API_URL}/stock/${encodeURIComponent(query)}`);
      
      if (response.data.suggestions) {
        setSuggestions(response.data.suggestions);
        setSelectedCompany(null);
        setStockHistory([]);
        setStockMetrics(null);
      } else {
        setSelectedCompany(response.data.company_name);
        setStockHistory(response.data.history || []);
        setStockMetrics(response.data.metrics || null);
        setTimeframe("1Y");
        setCompany("");
        setPredictedData([]);
      }
    } catch (error) {
      console.error("Error during search:", error);
      setSuggestions([]);
      setSelectedCompany(null);
      setStockHistory([]);
      setStockMetrics(null);
    } finally {
      setIsLoading(false);
    }
  };

  const fetchHistoryForTimeframe = async (companyName, newTimeframe) => {
    setIsLoading(true);
    try {
        const response = await axios.get(
            `${process.env.NEXT_PUBLIC_API_URL}/stock/history/${encodeURIComponent(companyName)}?timeframe=${newTimeframe}`
        );
        if (response.data?.history) {
            setStockHistory(response.data.history);
            setTimeframe(newTimeframe);
        }
    } catch (error) {
        console.error("Error fetching new timeframe:", error);
    } finally {
        setIsLoading(false);
    }
  };

  const handleTimeframeChange = (newTimeframe) => {
      if (selectedCompany) {
          fetchHistoryForTimeframe(selectedCompany, newTimeframe);
      }
  };

  const handlePredict = async () => {
    if (!selectedCompany) return;
    setIsPredicting(true);
    try {
      // Pass the selected modelType to the API
      const response = await axios.get(
        `${process.env.NEXT_PUBLIC_API_URL}/stock/predict/${encodeURIComponent(selectedCompany)}?timeframe=${predictedTimeframe}&model_type=${modelType}`
      );
      if (response.data?.predictions) {
        setPredictedData(response.data.predictions);
      }
    } catch (err) {
      console.error("Error predicting stock price:", err);
    } finally {
        setIsPredicting(false);
    }
  };

  // --- Display Helpers ---
  const formatMarketCap = (cap) => {
    if (!cap) return "N/A";
    if (cap > 1e12) return `$${(cap / 1e12).toFixed(2)}T`;
    if (cap > 1e9) return `$${(cap / 1e9).toFixed(2)}B`;
    return `$${(cap / 1e6).toFixed(2)}M`;
  };
  
  const getPriceChange = () => {
      if(stockHistory.length < 2) return null;
      const startPrice = stockHistory[0].close;
      const endPrice = stockHistory[stockHistory.length-1].close;
      const absoluteChange = endPrice - startPrice;
      const percentageChange = (absoluteChange / startPrice) * 100;
      const isPositive = absoluteChange >= 0;
      return {
          absolute: absoluteChange.toFixed(2),
          percent: percentageChange.toFixed(2),
          isPositive,
      }
  }
  const priceChange = getPriceChange();

  // --- Render ---
  return (
    <div className="bg-slate-950 text-white min-h-screen p-4 sm:p-6 lg:p-8">
      <div className="max-w-7xl mx-auto grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* LEFT COLUMN */}
        <div className="lg:col-span-1 flex flex-col gap-6">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <TrendingUp className="text-teal-400" />
                Stock Price Finder
              </CardTitle>
              <CardDescription>
                Enter a company name or ticker to begin.
              </CardDescription>
            </CardHeader>
            <CardContent className="flex flex-col gap-4">
              <div className="flex gap-2">
                <Input
                  type="text"
                  value={company}
                  onChange={(e) => setCompany(e.target.value)}
                  onKeyDown={(e) => e.key === "Enter" && handleSearch()}
                  placeholder="e.g., Apple or AAPL"
                />
                <Button onClick={() => handleSearch()} disabled={!company || isLoading}>
                  <Search size={16} />
                </Button>
              </div>
              {suggestions.length > 0 && (
                <div className="flex flex-col gap-2">
                    {suggestions.map(s => (
                        <Button key={s.ticker} variant="ghost" className="justify-start" onClick={() => handleSearch(s.name)}>
                            {s.name} ({s.ticker})
                        </Button>
                    ))}
                </div>
              )}
              <Dialog open={showAllCompaniesOpen} onOpenChange={setShowAllCompaniesOpen}>
                <DialogTrigger asChild>
                  <Button variant="outline" className="w-full">
                    <ChevronsUpDown className="mr-2 h-4 w-4" /> Show All Companies
                  </Button>
                </DialogTrigger>
                <DialogContent className="max-w-xl max-h-[80vh] overflow-y-auto">
                  <DialogHeader>
                    <DialogTitle>All Companies</DialogTitle>
                    <DialogDescription>Select a company to view its data.</DialogDescription>
                  </DialogHeader>
                  <Table>
                    <TableHeader>
                      <TableRow>
                        <TableHead>Company Name</TableHead>
                      </TableRow>
                    </TableHeader>
                    <TableBody>
                        {companyList.map((name) => (
                            <TableRow key={name} className="cursor-pointer hover:bg-muted/50" onClick={() => { handleSearch(name); setShowAllCompaniesOpen(false); }}>
                                <TableCell>{name}</TableCell>
                            </TableRow>
                        ))}
                    </TableBody>
                  </Table>
                </DialogContent>
              </Dialog>
            </CardContent>
          </Card>

          {selectedCompany && !isLoading && (
            <Card>
              <CardHeader>
                <CardTitle>{selectedCompany}</CardTitle>
                 {currentPrice && <CardDescription className="text-2xl font-bold text-foreground">${currentPrice.toFixed(2)}</CardDescription>}
                 {priceChange && (
                     <p className={`text-sm font-medium ${priceChange.isPositive ? 'text-green-400' : 'text-red-400'}`}>
                        {priceChange.isPositive ? '+' : ''}{priceChange.absolute} ({priceChange.percent}%) {timeframe}
                     </p>
                 )}
              </CardHeader>
              <CardContent className="flex flex-col gap-4">
                <div className="flex gap-2 flex-wrap">
                    {["1D", "1W", "1M", "6M", "1Y", "5Y", "Max"].map(tf => (
                        <Button key={tf} variant={timeframe === tf ? "secondary" : "outline"} size="sm" onClick={() => handleTimeframeChange(tf)}>
                            {tf}
                        </Button>
                    ))}
                </div>
                <div className="space-y-2 pt-4">
                  <Stat label="Market Cap" value={formatMarketCap(stockMetrics?.marketCap)} />
                  <Stat label="Volume (Avg)" value={stockMetrics?.averageVolume?.toLocaleString()} />
                  <Stat label="P/E Ratio" value={stockMetrics?.trailingPE?.toFixed(2)} />
                  <Stat label="Dividend Yield" value={stockMetrics?.dividendYield ? `${(stockMetrics.dividendYield * 100).toFixed(2)}%` : 'N/A'} />
                  <Stat label="52-Week Range" value={stockMetrics ? `$${stockMetrics.fiftyTwoWeekLow?.toFixed(2)} - $${stockMetrics.fiftyTwoWeekHigh?.toFixed(2)}` : 'N/A'} />
                </div>
              </CardContent>
            </Card>
          )}
        </div>

        {/* RIGHT COLUMN */}
        <div className="lg:col-span-2 flex flex-col gap-6">
          <Card className="flex-grow flex flex-col">
            <CardHeader>
              <CardTitle>Historical Performance</CardTitle>
            </CardHeader>
            <CardContent className="flex-grow">
              {stockHistory.length > 0 && !isLoading ? (
                <ResponsiveContainer width="100%" height="100%">
                  <LineChart data={stockHistory} margin={{ top: 5, right: 20, left: -10, bottom: 5 }}>
                    <CartesianGrid stroke="hsl(var(--border))" strokeDasharray="3 3" />
                    <XAxis 
                      dataKey="date" 
                      tick={{ fontSize: 12 }} 
                      stroke="hsl(var(--muted-foreground))" 
                      tickLine={false}
                      tickFormatter={(value) => formatDate(value, timeframe)}
                    />
                    <YAxis 
                      tickFormatter={(value) => `$${value}`} 
                      tick={{ fontSize: 12 }} 
                      stroke="hsl(var(--muted-foreground))" 
                      tickLine={false} 
                      axisLine={false} 
                      domain={['dataMin - 5', 'dataMax + 5']}
                    />
                    <Tooltip
                        contentStyle={{
                            background: "hsl(var(--background))",
                            borderColor: "hsl(var(--border))",
                        }}
                    />
                    <Line type="monotone" dataKey="close" stroke="#60a5fa" strokeWidth={2} dot={false} />
                  </LineChart>
                </ResponsiveContainer>
              ) : <div className="flex items-center justify-center h-full text-muted-foreground">{isLoading ? "Loading..." : "Select a company to view its chart."}</div>}
            </CardContent>
          </Card>
          
          <Card>
            <CardHeader>
                <CardTitle>AI Price Prediction</CardTitle>
                <CardDescription>Predict future prices using a machine learning model.</CardDescription>
            </CardHeader>
            <CardContent className="flex flex-col gap-4">
                <div>
                    <p className="text-sm font-medium mb-2 text-muted-foreground">1. Select Model</p>
                    <div className="flex gap-2">
                        <Button variant={modelType === 'linear' ? "secondary" : "outline"} onClick={() => setModelType('linear')}>Linear Regression</Button>
                        <Button variant={modelType === 'tree' ? "secondary" : "outline"} onClick={() => setModelType('tree')}>Decision Tree</Button>
                    </div>
                </div>
                <div>
                    <p className="text-sm font-medium mb-2 text-muted-foreground">2. Select Timeframe & Predict</p>
                    <div className="flex flex-col sm:flex-row items-start sm:items-center gap-4">
                        <div className="flex gap-2">
                            {["1D", "1W", "1M"].map(tf => (
                                <Button key={tf} variant={predictedTimeframe === tf ? "secondary" : "outline"} size="sm" onClick={() => setPredictedTimeframe(tf)}>
                                    {tf}
                                </Button>
                            ))}
                        </div>
                        <Button onClick={handlePredict} disabled={isPredicting || !selectedCompany}>
                            {isPredicting ? "Predicting..." : `Predict ${predictedTimeframe} Ahead`}
                        </Button>
                    </div>
                </div>
            </CardContent>
            {predictedData.length > 0 && (
              <CardContent>
                  <div className="h-60">
                    <ResponsiveContainer width="100%" height="100%">
                        <LineChart data={[...stockHistory.slice(-30), ...predictedData]} margin={{ top: 5, right: 20, left: -10, bottom: 5 }}>
                            <CartesianGrid stroke="hsl(var(--border))" strokeDasharray="3 3" />
                            <XAxis 
                              dataKey="date" 
                              tick={{ fontSize: 12 }} 
                              stroke="hsl(var(--muted-foreground))" 
                              tickLine={false} 
                              tickFormatter={(value) => formatDate(value, '1M')}
                            />
                            <YAxis 
                              tickFormatter={(value) => `$${value}`} 
                              tick={{ fontSize: 12 }} 
                              stroke="hsl(var(--muted-foreground))" 
                              tickLine={false} 
                              axisLine={false} 
                              domain={['dataMin - 5', 'dataMax + 5']}
                            />
                            <Tooltip
                              contentStyle={{
                                  background: "hsl(var(--background))",
                                  borderColor: "hsl(var(--border))",
                              }}
                          />
                            <Line type="monotone" dataKey="close" stroke="#60a5fa" strokeWidth={2} dot={false} />
                            <ReferenceLine x={predictedData[0]?.date} stroke="hsl(var(--border))" strokeDasharray="3 3" />
                        </LineChart>
                    </ResponsiveContainer>
                  </div>
              </CardContent>
            )}
          </Card>
        </div>
      </div>
    </div>
  );
}