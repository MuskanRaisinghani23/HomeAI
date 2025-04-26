import { useEffect } from "react";

export default function AnalyticsDashboard() {
  useEffect(() => {
    const script = document.createElement("script");
    script.src = "https://public.tableau.com/javascripts/api/viz_v1.js";
    script.type = "text/javascript";
    document.body.appendChild(script);
  }, []);

  return (
    <div className="analytics-page" style={{ minHeight: '100vh', padding: '10px', backgroundColor: '#f9f9f9' }}>
      <h2 style={{ marginLeft: '20px', marginBottom: '20px' }}>HomeAI Insights Center</h2>
      
      <div style={{ display: 'flex', justifyContent: 'center' }}>
        <div
          className="tableauPlaceholder"
          id="viz1745659352920"
          style={{ width: '80%', height: '90vh', position: "relative" }}
          dangerouslySetInnerHTML={{
            __html: `
              <noscript>
                <a href='#'>
                  <img alt='HomeAI Analysis Dashboard' src='https://public.tableau.com/static/images/Ho/HomeAIdashboard/HomeAIAnalysisDashboard/1_rss.png' style='border: none' />
                </a>
              </noscript>
              <object class='tableauViz' style='width: 100%; height: 100%; display: block;'>
                <param name='host_url' value='https%3A%2F%2Fpublic.tableau.com%2F' />
                <param name='embed_code_version' value='3' />
                <param name='site_root' value=''/>
                <param name='name' value='HomeAIdashboard/HomeAIAnalysisDashboard' />
                <param name='tabs' value='no'/>
                <param name='toolbar' value='yes'/>
                <param name='static_image' value='https://public.tableau.com/static/images/Ho/HomeAIdashboard/HomeAIAnalysisDashboard/1.png' />
                <param name='animate_transition' value='yes'/>
                <param name='display_static_image' value='yes'/>
                <param name='display_spinner' value='yes'/>
                <param name='display_overlay' value='yes'/>
                <param name='display_count' value='yes'/>
                <param name='language' value='en-US'/>
                <param name='filter' value='publish=yes'/>
              </object>
            `,
          }}
        ></div>
      </div>
    </div>
  );
}
