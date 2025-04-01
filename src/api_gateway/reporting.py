from typing import Dict, List, Optional
from pydantic import BaseModel
from datetime import datetime, timedelta
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from fastapi import HTTPException
import json
import os

class ReportTemplate(BaseModel):
    name: str
    description: str
    metrics: List[str]
    visualizations: List[str]
    frequency: str
    format: str

class ReportManager:
    def __init__(self):
        self.templates_dir = "configs/report_templates"
        self.reports_dir = "data/reports"
        os.makedirs(self.templates_dir, exist_ok=True)
        os.makedirs(self.reports_dir, exist_ok=True)

    async def create_template(self, user_id: str, template: ReportTemplate) -> Dict:
        """Create a custom report template"""
        try:
            template_path = self._get_template_path(user_id, template.name)
            with open(template_path, 'w') as f:
                json.dump(template.dict(), f)
            return {"status": "success", "template": template}
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to create template: {str(e)}")

    async def generate_report(self, user_id: str, template_name: str, data: Dict) -> Dict:
        """Generate a custom report using template"""
        try:
            # Load template
            template = await self.get_template(user_id, template_name)
            if not template:
                raise HTTPException(status_code=404, detail="Template not found")

            # Process data according to template
            processed_data = self._process_data(data, template.metrics)
            
            # Generate visualizations
            visualizations = self._create_visualizations(processed_data, template.visualizations)
            
            # Format report
            report = self._format_report(processed_data, visualizations, template)
            
            # Save report
            report_path = self._save_report(user_id, template_name, report)
            
            return {
                "status": "success",
                "report_url": report_path,
                "report_data": report
            }
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to generate report: {str(e)}")

    def _process_data(self, data: Dict, metrics: List[str]) -> Dict:
        """Process raw data according to specified metrics"""
        processed = {}
        for metric in metrics:
            if metric in data:
                if metric == "roi":
                    processed[metric] = self._calculate_roi(data[metric])
                elif metric == "market_trends":
                    processed[metric] = self._analyze_trends(data[metric])
                elif metric == "comparables":
                    processed[metric] = self._process_comps(data[metric])
                else:
                    processed[metric] = data[metric]
        return processed

    def _create_visualizations(self, data: Dict, viz_types: List[str]) -> Dict:
        """Create specified visualizations from processed data"""
        visualizations = {}
        for viz_type in viz_types:
            if viz_type == "price_trend":
                visualizations[viz_type] = self._create_price_trend_chart(data)
            elif viz_type == "market_comparison":
                visualizations[viz_type] = self._create_market_comparison(data)
            elif viz_type == "roi_analysis":
                visualizations[viz_type] = self._create_roi_analysis(data)
        return visualizations

    def _create_price_trend_chart(self, data: Dict) -> Dict:
        """Create price trend visualization"""
        if "market_trends" not in data:
            return None
            
        df = pd.DataFrame(data["market_trends"])
        fig = px.line(df, x="date", y="price", title="Price Trends")
        return fig.to_dict()

    def _create_market_comparison(self, data: Dict) -> Dict:
        """Create market comparison visualization"""
        if "comparables" not in data:
            return None
            
        df = pd.DataFrame(data["comparables"])
        fig = px.box(df, y="price", title="Market Price Distribution")
        return fig.to_dict()

    def _create_roi_analysis(self, data: Dict) -> Dict:
        """Create ROI analysis visualization"""
        if "roi" not in data:
            return None
            
        roi_data = data["roi"]
        fig = go.Figure(data=[
            go.Bar(name="Costs", x=["Purchase", "Repairs", "Holding"], y=[
                roi_data["purchase_cost"],
                roi_data["repair_cost"],
                roi_data["holding_cost"]
            ]),
            go.Bar(name="Returns", x=["Sale Price", "Net Profit"], y=[
                roi_data["sale_price"],
                roi_data["net_profit"]
            ])
        ])
        return fig.to_dict()

    def _format_report(self, data: Dict, visualizations: Dict, template: ReportTemplate) -> Dict:
        """Format the final report according to template"""
        report = {
            "generated_at": datetime.utcnow().isoformat(),
            "template_name": template.name,
            "metrics": data,
            "visualizations": visualizations,
            "summary": self._generate_summary(data)
        }
        
        return report

    def _generate_summary(self, data: Dict) -> str:
        """Generate natural language summary of the report"""
        summary = []
        
        if "roi" in data:
            roi = data["roi"]
            summary.append(f"Expected ROI: {roi['percentage']}%")
            summary.append(f"Net Profit: ${roi['net_profit']:,.2f}")
            
        if "market_trends" in data:
            trends = data["market_trends"]
            summary.append(f"Market Trend: {trends['direction']} ({trends['percentage']}% over {trends['period']})")
            
        if "comparables" in data:
            comps = data["comparables"]
            summary.append(f"Property ranks in the {comps['percentile']}th percentile for the area")
            
        return "\n".join(summary)

    async def get_template(self, user_id: str, template_name: str) -> Optional[ReportTemplate]:
        """Get a report template"""
        try:
            template_path = self._get_template_path(user_id, template_name)
            if not os.path.exists(template_path):
                return None
            with open(template_path, 'r') as f:
                template_data = json.load(f)
            return ReportTemplate(**template_data)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to load template: {str(e)}")

    def _get_template_path(self, user_id: str, template_name: str) -> str:
        """Get path to template file"""
        return os.path.join(self.templates_dir, f"{user_id}_{template_name}.json")

    def _save_report(self, user_id: str, template_name: str, report: Dict) -> str:
        """Save generated report"""
        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        report_path = os.path.join(
            self.reports_dir,
            f"{user_id}_{template_name}_{timestamp}.json"
        )
        
        with open(report_path, 'w') as f:
            json.dump(report, f)
            
        return report_path
