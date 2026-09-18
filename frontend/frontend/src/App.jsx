import { useEffect, useMemo, useState } from "react";
import axios from "axios";

import {
  LayoutDashboard,
  Users,
  TrendingUp,
  Package,
  FileText,
  Bell,
  Settings,
  Search,
  Activity,
  RefreshCw,
  ExternalLink,
  CheckCircle2,
  Clock3,
} from "lucide-react";

import "./App.css";


const API_URL = "http://127.0.0.1:8000";


const competitors = [
  {
    key: "reliance",
    name: "Reliance Digital",
    short: "RD",
  },
  {
    key: "vijay_sales",
    name: "Vijay Sales",
    short: "VS",
  },
  {
    key: "croma",
    name: "Croma",
    short: "CR",
  },
];


function App() {

  const [activePage, setActivePage] = useState("Overview");

  const [dashboard, setDashboard] = useState(null);

  const [loading, setLoading] = useState(true);

  const [error, setError] = useState("");

  const [selectedCompetitor, setSelectedCompetitor] =
    useState("reliance");

  const [productSearch, setProductSearch] = useState("");

  const [priceMovements, setPriceMovements] =
    useState(null);

  const [reports, setReports] =
    useState(null);


  // --------------------------------
  // FETCH DASHBOARD
  // --------------------------------

  const fetchDashboard = async () => {

    try {

      setLoading(true);
      setError("");

      const response = await axios.get(
        `${API_URL}/dashboard`
      );

      setDashboard(response.data);

    } catch (err) {

      console.error(err);

      setError(
        "Unable to connect to the intelligence backend."
      );

    } finally {

      setLoading(false);

    }
  };


  // --------------------------------
  // FETCH PRICE MOVEMENTS
  // --------------------------------

  const fetchPriceMovements = async () => {

    try {

      const response = await axios.get(
        `${API_URL}/price-movements`
      );

      setPriceMovements(response.data);

    } catch (err) {

      console.error(err);

    }
  };


  // --------------------------------
  // FETCH REPORTS
  // --------------------------------

  const fetchReports = async () => {

    try {

      const response = await axios.get(
        `${API_URL}/reports`
      );

      setReports(response.data);

    } catch (err) {

      console.error(err);

    }
  };


  // --------------------------------
  // INITIAL LOAD
  // --------------------------------

  useEffect(() => {

    fetchDashboard();

    fetchPriceMovements();

    fetchReports();

  }, []);


  // --------------------------------
  // TOTAL PRODUCTS
  // --------------------------------

  const totalProducts = useMemo(() => {

    if (!dashboard) {
      return 0;
    }

    return Object.values(dashboard).reduce(
      (total, retailer) =>
        total + (retailer.count || 0),
      0
    );

  }, [dashboard]);


  // --------------------------------
  // OVERVIEW
  // --------------------------------

  const renderOverview = () => {

    return (
      <>

        <section className="hero">

          <div>

            <div className="section-label">
              RELIANCE DIGITAL INTELLIGENCE
            </div>

            <h1>
              Competitive intelligence,
              <br />
              without the noise.
            </h1>

            <p>
              Automated monitoring across major
              electronics retailers.
            </p>

          </div>

          <div className="hero-status">

            <div className="status-dot"></div>

            <span>
              LIVE DATA
            </span>

          </div>

        </section>


        <section className="section">

          <div className="section-heading">

            <div>

              <div className="section-label">
                MARKET OVERVIEW
              </div>

              <h2>
                Current catalogue coverage
              </h2>

            </div>

            <button
              className="refresh-button"
              onClick={() => {

                fetchDashboard();
                fetchPriceMovements();
                fetchReports();

              }}
            >

              <RefreshCw size={14} />

              Refresh

            </button>

          </div>


          <div className="competitor-grid">

            {competitors.map((competitor) => {

              const data =
                dashboard?.[competitor.key];

              return (

                <div
                  className="competitor-card"
                  key={competitor.key}
                >

                  <div className="competitor-top">

                    <div className="competitor-logo">
                      {competitor.short}
                    </div>

                    <Activity size={15} />

                  </div>

                  <div className="competitor-name">
                    {competitor.name}
                  </div>

                  <div className="competitor-count">
                    {data?.count ?? 0}
                  </div>

                  <div className="competitor-label">
                    PRODUCTS TRACKED
                  </div>

                </div>

              );

            })}

          </div>

        </section>


        <section className="section">

          <div className="section-heading">

            <div>

              <div className="section-label">
                DATA PIPELINE
              </div>

              <h2>
                Intelligence coverage
              </h2>

            </div>

          </div>


          <div className="pipeline-grid">

            <div className="pipeline-card">

              <Package size={18} />

              <strong>
                {totalProducts}
              </strong>

              <span>
                PRODUCTS
              </span>

            </div>


            <div className="pipeline-card">

              <Users size={18} />

              <strong>
                3
              </strong>

              <span>
                RETAILERS
              </span>

            </div>


            <div className="pipeline-card">

              <TrendingUp size={18} />

              <strong>
                24h
              </strong>

              <span>
                REFRESH CYCLE
              </span>

            </div>

          </div>

        </section>

      </>
    );

  };


  // --------------------------------
  // COMPETITORS
  // --------------------------------

  const renderCompetitors = () => {

    const competitor =
      competitors.find(
        (item) =>
          item.key === selectedCompetitor
      );

    const products =
      dashboard?.[selectedCompetitor]?.products ||
      [];


    const filteredProducts =
      products.filter((product) => {

        const search =
          productSearch.toLowerCase();

        return (

          product.name
            ?.toLowerCase()
            .includes(search) ||

          product.product_name
            ?.toLowerCase()
            .includes(search) ||

          product.brand
            ?.toLowerCase()
            .includes(search) ||

          product.category
            ?.toLowerCase()
            .includes(search)

        );

      });


    return (

      <section className="section">

        <div className="section-heading">

          <div>

            <div className="section-label">
              COMPETITIVE ACTIVITY
            </div>

            <h2>
              Competitor catalogues
            </h2>

          </div>

        </div>


        <div className="competitor-selector">

          {competitors.map((item) => (

            <button
              key={item.key}
              className={
                selectedCompetitor === item.key
                  ? "competitor-selector-button active"
                  : "competitor-selector-button"
              }
              onClick={() => {

                setSelectedCompetitor(item.key);
                setProductSearch("");

              }}
            >

              <span>
                {item.short}
              </span>

              <strong>
                {item.name}
              </strong>

            </button>

          ))}

        </div>


        <div className="product-toolbar">

          <div className="product-search">

            <Search size={16} />

            <input
              type="text"
              placeholder="Search products..."
              value={productSearch}
              onChange={(e) =>
                setProductSearch(e.target.value)
              }
            />

          </div>

        </div>


        <div className="product-summary">

          <div>

            <span>
              RETAILER
            </span>

            <strong>
              {competitor?.name}
            </strong>

          </div>


          <div>

            <span>
              PRODUCTS
            </span>

            <strong>
              {filteredProducts.length}
            </strong>

          </div>

        </div>


        <div className="products-table-wrapper">

          <table className="products-table">

            <thead>

              <tr>

                <th>PRODUCT</th>
                <th>BRAND</th>
                <th>CATEGORY</th>
                <th>PRICE</th>
                <th>SOURCE</th>

              </tr>

            </thead>


            <tbody>

              {filteredProducts.map(
                (product, index) => (

                  <tr
                    key={
                      `${product.source_url}-${index}`
                    }
                  >

                    <td>
                      <div className="product-name">
                        {product.name ||
                          product.product_name ||
                          "Unnamed product"}
                      </div>
                    </td>

                    <td>
                      {product.brand || "—"}
                    </td>

                    <td>
                      {product.category || "—"}
                    </td>

                    <td>
                      {product.price
                        ? `₹${product.price}`
                        : "—"}
                    </td>

                    <td>

                      {product.source_url ? (

                        <a
                          href={product.source_url}
                          target="_blank"
                          rel="noreferrer"
                          className="source-link"
                        >
                          View
                          <ExternalLink size={13} />
                        </a>

                      ) : (

                        "—"

                      )}

                    </td>

                  </tr>

                )
              )}


              {filteredProducts.length === 0 && (

                <tr>

                  <td
                    colSpan="5"
                    className="no-products"
                  >
                    No products found.
                  </td>

                </tr>

              )}

            </tbody>

          </table>

        </div>

      </section>

    );

  };


  // --------------------------------
  // PRICE MOVEMENTS
  // --------------------------------

  const renderPriceMovements = () => {

    if (!priceMovements?.available) {

      return (

        <section className="empty-intelligence">

          <div className="empty-icon">
            <TrendingUp size={22} />
          </div>

          <div className="section-label">
            PRICE INTELLIGENCE
          </div>

          <h2>
            Waiting for comparison data
          </h2>

          <p>
            Price movements will appear here
            after the next automated snapshot
            is created.
          </p>

          <div className="empty-meta">
            <span>Current snapshot</span>
            <strong>Available</strong>
          </div>

          <div className="empty-meta">
            <span>Previous snapshot</span>
            <strong>Waiting</strong>
          </div>

          <div className="empty-meta">
            <span>Comparison</span>
            <strong>Pending</strong>
          </div>

        </section>

      );

    }


    const report =
      priceMovements.report || {};

    const retailerData =
      report.retailers || {};


    const priceChanges = Object.values(
      retailerData
    ).flatMap(
      (retailer) =>
        retailer.price_changes || []
    );


    const verifiedChanges =
      priceChanges.filter(
        (change) =>
          change.name &&
          change.old_price != null &&
          change.new_price != null
      );


    return (

      <section className="section">

        <div className="section-heading">

          <div>

            <div className="section-label">
              PRICE INTELLIGENCE
            </div>

            <h2>
              Detected price movements
            </h2>

            <p className="section-subtitle">
              Verified price changes detected
              between the latest daily snapshots.
            </p>

          </div>

        </div>


        {verifiedChanges.length === 0 ? (

          <div className="empty-intelligence">

            <div className="empty-icon">
              <CheckCircle2 size={22} />
            </div>

            <div className="section-label">
              NO VERIFIED MOVEMENTS
            </div>

            <h2>
              No verified price movements detected
            </h2>

            <p>
              The latest snapshot comparison found
              no confirmed price changes across the
              monitored retailers.
            </p>


            <div className="empty-meta">

              <span>
                Comparison date
              </span>

              <strong>
                {report.today || "—"}
              </strong>

            </div>


            {competitors.map(
              (competitor) => {

                const data =
                  retailerData[
                    competitor.key
                  ];

                return (

                  <div
                    className="empty-meta"
                    key={competitor.key}
                  >

                    <span>
                      {competitor.name}
                    </span>

                    <strong>

                      {data?.status ===
                      "source_unavailable"

                        ? "Source unavailable"

                        : `${data?.price_changes?.length || 0} changes`
                      }

                    </strong>

                  </div>

                );

              }
            )}

          </div>

        ) : (

          <div className="price-change-list">

            {verifiedChanges.map(
              (change, index) => {

                const increase =
                  change.difference > 0;

                return (

                  <div
                    className="price-change-card"
                    key={
                      `${change.source_url}-${index}`
                    }
                  >

                    <div className="price-change-top">

                      <div>

                        <div className="section-label">
                          {change.category ||
                            "PRODUCT"}
                        </div>

                        <h3>
                          {change.name}
                        </h3>

                      </div>

                      <TrendingUp
                        size={18}
                      />

                    </div>


                    <div className="price-change-values">

                      <div>

                        <span>
                          PREVIOUS
                        </span>

                        <strong>
                          ₹
                          {change.old_price.toLocaleString(
                            "en-IN"
                          )}
                        </strong>

                      </div>


                      <div>

                        <span>
                          CURRENT
                        </span>

                        <strong>
                          ₹
                          {change.new_price.toLocaleString(
                            "en-IN"
                          )}
                        </strong>

                      </div>


                      <div>

                        <span>
                          CHANGE
                        </span>

                        <strong>
                          {increase
                            ? "+"
                            : ""}
                          ₹
                          {Math.abs(
                            change.difference
                          ).toLocaleString(
                            "en-IN"
                          )}

                          {" "}

                          (
                          {increase
                            ? "+"
                            : ""}
                          {Number(
                            change.percentage
                          ).toFixed(1)}
                          %)
                        </strong>

                      </div>

                    </div>


                    {change.source_url && (

                      <a
                        href={
                          change.source_url
                        }
                        target="_blank"
                        rel="noreferrer"
                        className="source-link"
                      >
                        View source
                        <ExternalLink
                          size={13}
                        />
                      </a>

                    )}

                  </div>

                );

              }
            )}

          </div>

        )}

      </section>

    );

  };


  // --------------------------------
  // PRODUCTS
  // --------------------------------

  const renderProducts = () => {

    const competitor =
      competitors.find(
        (item) =>
          item.key === selectedCompetitor
      );


    const products =
      dashboard?.[selectedCompetitor]?.products ||
      [];


    const filteredProducts =
      products.filter((product) => {

        const search =
          productSearch.toLowerCase();

        return (

          product.name
            ?.toLowerCase()
            .includes(search) ||

          product.product_name
            ?.toLowerCase()
            .includes(search) ||

          product.brand
            ?.toLowerCase()
            .includes(search) ||

          product.category
            ?.toLowerCase()
            .includes(search)

        );

      });


    const categories = [
      ...new Set(
        products
          .map(
            (product) =>
              product.category
          )
          .filter(Boolean)
      ),
    ];


    return (

      <section className="section">

        <div className="section-heading">

          <div>

            <div className="section-label">
              PRODUCT INTELLIGENCE
            </div>

            <h2>
              Tracked products
            </h2>

            <p className="section-subtitle">
              Live catalogue data collected
              from competitor sources.
            </p>

          </div>

        </div>


        <div className="product-toolbar">

          <div className="product-search">

            <Search size={16} />

            <input
              type="text"
              placeholder="Search products, brands or categories..."
              value={productSearch}
              onChange={(e) =>
                setProductSearch(e.target.value)
              }
            />

          </div>


          <div className="product-retailers">

            {competitors.map((item) => (

              <button
                key={item.key}
                className={
                  selectedCompetitor === item.key
                    ? "retailer-filter active"
                    : "retailer-filter"
                }
                onClick={() => {

                  setSelectedCompetitor(item.key);
                  setProductSearch("");

                }}
              >

                {item.short}

              </button>

            ))}

          </div>

        </div>


        <div className="product-summary">

          <div>

            <span>RETAILER</span>

            <strong>
              {competitor?.name}
            </strong>

          </div>


          <div>

            <span>PRODUCTS</span>

            <strong>
              {filteredProducts.length}
            </strong>

          </div>


          <div>

            <span>CATEGORIES</span>

            <strong>
              {categories.length}
            </strong>

          </div>

        </div>


        <div className="products-table-wrapper">

          <table className="products-table">

            <thead>

              <tr>

                <th>PRODUCT</th>
                <th>BRAND</th>
                <th>CATEGORY</th>
                <th>PRICE</th>
                <th>SOURCE</th>

              </tr>

            </thead>


            <tbody>

              {filteredProducts.map(
                (product, index) => (

                  <tr
                    key={
                      `${product.source_url}-${index}`
                    }
                  >

                    <td>

                      <div className="product-name">
                        {product.name ||
                          product.product_name ||
                          "Unnamed product"}
                      </div>

                    </td>

                    <td>
                      {product.brand || "—"}
                    </td>

                    <td>
                      {product.category || "—"}
                    </td>

                    <td>
                      {product.price
                        ? `₹${product.price}`
                        : "—"}
                    </td>

                    <td>

                      {product.source_url ? (

                        <a
                          href={product.source_url}
                          target="_blank"
                          rel="noreferrer"
                          className="source-link"
                        >
                          View
                          <ExternalLink size={13} />
                        </a>

                      ) : (

                        "—"

                      )}

                    </td>

                  </tr>

                )
              )}


              {filteredProducts.length === 0 && (

                <tr>

                  <td
                    colSpan="5"
                    className="no-products"
                  >
                    No products found.
                  </td>

                </tr>

              )}

            </tbody>

          </table>

        </div>

      </section>

    );

  };


  // --------------------------------
  // REPORTS
  // --------------------------------

  const renderReports = () => {

    const dailyReports =
      reports?.daily_reports || [];

    const comparisonReports =
      reports?.comparison_reports || [];


    return (

      <section className="section">

        <div className="section-heading">

          <div>

            <div className="section-label">
              INTELLIGENCE REPORTS
            </div>

            <h2>
              Generated reports
            </h2>

            <p className="section-subtitle">
              Automated competitor intelligence
              reports generated from snapshot
              comparisons.
            </p>

          </div>

        </div>


        <div className="reports-grid">

          <div className="reports-card">

            <div className="reports-card-top">

              <FileText size={18} />

              <span>
                DAILY REPORTS
              </span>

            </div>


            <div className="reports-count">
              {dailyReports.length}
            </div>


            <div className="reports-description">
              Generated HTML intelligence reports.
            </div>


            <div className="reports-list">

              {dailyReports.length === 0 ? (

                <div className="report-empty">
                  No daily report generated yet.
                </div>

              ) : (

                dailyReports.map((report) => (

                  <div
                    className="report-row"
                    key={report.name}
                  >

                    <div>

                      <strong>
                        {report.date}
                      </strong>

                      <span>
                        Daily intelligence report
                      </span>

                    </div>

                  </div>

                ))

              )}

            </div>

          </div>


          <div className="reports-card">

            <div className="reports-card-top">

              <Activity size={18} />

              <span>
                SNAPSHOT COMPARISONS
              </span>

            </div>


            <div className="reports-count">
              {comparisonReports.length}
            </div>


            <div className="reports-description">
              Product and price changes detected
              between snapshots.
            </div>


            <div className="reports-list">

              {comparisonReports.length === 0 ? (

                <div className="report-empty">

                  Waiting for the second snapshot.

                  <small>
                    A comparison requires two
                    daily snapshots.
                  </small>

                </div>

              ) : (

                comparisonReports.map((report) => (

                  <div
                    className="report-row"
                    key={report.name}
                  >

                    <div>

                      <strong>
                        {report.date}
                      </strong>

                      <span>
                        Snapshot comparison
                      </span>

                    </div>

                  </div>

                ))

              )}

            </div>

          </div>

        </div>

      </section>

    );

  };


  // --------------------------------
  // ALERTS
  // --------------------------------

  const renderAlerts = () => {

    const hasComparison =
      priceMovements?.available === true;

    const comparisonCount =
      reports?.comparison_reports?.length || 0;


    return (

      <section className="section">

        <div className="section-heading">

          <div>

            <div className="section-label">
              MONITORING
            </div>

            <h2>
              Alerts & triggers
            </h2>

            <p className="section-subtitle">
              Automated signals generated from
              competitor snapshot changes.
            </p>

          </div>

        </div>


        <div className="alerts-grid">

          <div className="alert-card">

            <div className="alert-icon">

              {hasComparison ? (
                <Bell size={19} />
              ) : (
                <Clock3 size={19} />
              )}

            </div>


            <div className="alert-content">

              <div className="section-label">
                PRICE CHANGES
              </div>

              <h3>
                {hasComparison
                  ? "Comparison available"
                  : "Monitoring active"}
              </h3>

              <p>
                {hasComparison
                  ? "The latest snapshot comparison is available for review."
                  : "Price-change alerts will activate after the second daily snapshot."}
              </p>

            </div>

          </div>


          <div className="alert-card">

            <div className="alert-icon">

              {comparisonCount > 0 ? (
                <CheckCircle2 size={19} />
              ) : (
                <Clock3 size={19} />
              )}

            </div>


            <div className="alert-content">

              <div className="section-label">
                SNAPSHOT STATUS
              </div>

              <h3>
                {comparisonCount > 0
                  ? "Comparison generated"
                  : "Waiting for comparison"}
              </h3>

              <p>
                {comparisonCount > 0
                  ? `${comparisonCount} comparison report(s) are available.`
                  : "Two dated snapshots are required before changes can be detected."}
              </p>

            </div>

          </div>


          <div className="alert-card">

            <div className="alert-icon">
              <Activity size={19} />
            </div>


            <div className="alert-content">

              <div className="section-label">
                DATA PIPELINE
              </div>

              <h3>
                24h monitoring cycle
              </h3>

              <p>
                Retailer catalogues are monitored
                through the scheduled scraping pipeline.
              </p>

            </div>

          </div>

        </div>


        <div className="alerts-status">

          <div>

            <span className="status-dot"></span>

            <strong>
              Monitoring system active
            </strong>

          </div>

          <span>
            {totalProducts} products currently tracked
          </span>

        </div>

      </section>

    );

  };


  // --------------------------------
  // PAGE SWITCHING
  // --------------------------------

  const renderPage = () => {

    if (activePage === "Competitors") {
      return renderCompetitors();
    }

    if (activePage === "Price Movements") {
      return renderPriceMovements();
    }

    if (activePage === "Products") {
      return renderProducts();
    }

    if (activePage === "Reports") {
      return renderReports();
    }

    if (activePage === "Alerts") {
      return renderAlerts();
    }

    return renderOverview();

  };


  // --------------------------------
  // MAIN JSX
  // --------------------------------

  return (

    <div className="app">


      <aside className="sidebar">

        <div className="sidebar-logo">
          RD
        </div>


        <div className="sidebar-title">
          CONTROL DECK
        </div>


        <nav className="sidebar-nav">

          <button
            className={
              activePage === "Overview"
                ? "nav-item active"
                : "nav-item"
            }
            onClick={() =>
              setActivePage("Overview")
            }
          >
            <LayoutDashboard size={16} />
            Overview
          </button>


          <button
            className={
              activePage === "Competitors"
                ? "nav-item active"
                : "nav-item"
            }
            onClick={() =>
              setActivePage("Competitors")
            }
          >
            <Users size={16} />
            Competitors
          </button>


          <button
            className={
              activePage === "Price Movements"
                ? "nav-item active"
                : "nav-item"
            }
            onClick={() =>
              setActivePage("Price Movements")
            }
          >
            <TrendingUp size={16} />
            Price Movements
          </button>


          <button
            className={
              activePage === "Products"
                ? "nav-item active"
                : "nav-item"
            }
            onClick={() =>
              setActivePage("Products")
            }
          >
            <Package size={16} />
            Products
          </button>


          <button
            className={
              activePage === "Reports"
                ? "nav-item active"
                : "nav-item"
            }
            onClick={() =>
              setActivePage("Reports")
            }
          >
            <FileText size={16} />
            Reports
          </button>


          <button
            className={
              activePage === "Alerts"
                ? "nav-item active"
                : "nav-item"
            }
            onClick={() =>
              setActivePage("Alerts")
            }
          >
            <Bell size={16} />
            Alerts
          </button>


          <button
            className={
              activePage === "Settings"
                ? "nav-item active"
                : "nav-item"
            }
            onClick={() =>
              setActivePage("Settings")
            }
          >
            <Settings size={16} />
            Settings
          </button>

        </nav>


        <div className="sidebar-bottom">

          <div className="sidebar-status">

            <span className="status-dot"></span>

            Backend connected

          </div>

        </div>

      </aside>


      <main className="main-content">


        <header className="topbar">

          <div>

            <div className="topbar-label">
              INTELLIGENCE PLATFORM
            </div>

            <div className="topbar-title">
              Reliance Digital
            </div>

          </div>


          <div className="topbar-actions">

            <button
              className="topbar-refresh"
              onClick={() => {

                fetchDashboard();
                fetchPriceMovements();
                fetchReports();

              }}
            >

              <RefreshCw size={14} />

              Refresh data

            </button>

          </div>

        </header>


        {loading && (

          <div className="loading-state">

            <RefreshCw
              size={20}
              className="loading-spin"
            />

            Loading intelligence data...

          </div>

        )}


        {error && (

          <div className="error-state">

            <strong>
              Backend connection failed
            </strong>

            <p>
              Make sure your FastAPI server
              is running on port 8000.
            </p>

            <button
              onClick={fetchDashboard}
            >
              Try again
            </button>

          </div>

        )}


        {!loading &&
          !error &&
          dashboard &&
          renderPage()}

      </main>

    </div>

  );

}


export default App;