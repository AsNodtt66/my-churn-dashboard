import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from matplotlib.gridspec import GridSpec
import numpy as np

# Load data
df = pd.read_csv('churn_results.csv', sep=';')  # Ganti dengan path file Anda jika perlu

# Bersihkan nama kolom
df.columns = df.columns.str.strip()

# Konversi tipe data
for col in ['TotalPrice', 'UnitPrice', 'Quantity', 'Recency']:
    df[col] = pd.to_numeric(df[col], errors='coerce')

df['CustomerID'] = df['CustomerID'].astype(int)

# Proxy variabel demografi
df['Gender'] = df['Churn'].map({1: 'Male', 0: 'Female'})  # Male = high risk/churned
age_bins = [0, 60, 120, 180, 240, 300, df['Recency'].max() + 1]
age_labels = ['18-30', '31-40', '41-50', '51-60', '61-70', '>71']
df['Age_Group'] = pd.cut(df['Recency'], bins=age_bins, labels=age_labels)

df['Income_Group'] = pd.cut(df['TotalPrice'], bins=5,
                            labels=['Low Income', 'Lower Middle', 'Middle', 'Upper Middle', 'High Income'])

df['Credit_Score'] = pd.cut(df['Quantity'], bins=5,
                            labels=['Poor', 'Fair', 'Good', 'Very Good', 'Excellent'])

df['Risk_Category'] = df['Predicted_Churn'].map({1: 'High Risk', 0: 'Low Risk'})

# Hitung metrics utama
total_clients = len(df)
male_count = df[df['Gender'] == 'Male'].shape[0]
female_count = df[df['Gender'] == 'Female'].shape[0]
avg_income = df['TotalPrice'].mean()
avg_recency = df['Recency'].mean()
per_capita = avg_income

# Setup figure aesthetic
sns.set_style("whitegrid")
plt.rcParams['font.family'] = 'DejaVu Sans'  # Atau 'sans-serif' jika DejaVu tidak tersedia
plt.rcParams['font.size'] = 12
fig = plt.figure(figsize=(28, 18), facecolor='#f0f4f8')
gs = GridSpec(5, 5, figure=fig, hspace=0.6, wspace=0.6)

# Palet warna aesthetic
pink = '#FF6B9D'
navy = '#2C3E50'
green = '#27AE60'
red = '#E74C3C'
pastel_colors = sns.color_palette("pastel", 5)
set2_colors = sns.color_palette("Set2", 5)

# Judul dashboard
fig.text(0.04, 0.96, 'DEMOGRAPHICS DASHBOARD', fontsize=32, fontweight='bold', color=navy, ha='left')
fig.text(0.04, 0.92, 'Evaluating Our Current Clients Demographics (Churn Proxy)', fontsize=18, color='#34495E', ha='left', style='italic')

# Border halus
fig.patch.set_edgecolor('#BDC3C7')
fig.patch.set_linewidth(2)

# 1. Total Clients
ax_total = fig.add_subplot(gs[0:2, 0])
ax_total.axis('off')
ax_total.add_patch(plt.Rectangle((0.1, 0.1), 0.8, 0.8, fill=True, facecolor='white', alpha=0.9, edgecolor=navy, linewidth=2))
ax_total.text(0.5, 0.7, f"{total_clients:,}", ha='center', va='center', fontsize=48, fontweight='bold', color=navy)
ax_total.text(0.5, 0.3, 'Total Clients', ha='center', va='center', fontsize=16, color='#555', fontweight='medium')

# 2. Gender Breakdown
ax_gender = fig.add_subplot(gs[0:2, 1])
bars = ax_gender.bar(['Female', 'Male'], [female_count, male_count], color=[pink, navy], width=0.7, edgecolor='white', linewidth=1)
ax_gender.set_title('Gender Breakdown', fontsize=18, pad=20, fontweight='bold', color=navy)
ax_gender.set_ylim(0, max(male_count, female_count) * 1.3)
ax_gender.grid(axis='y', linestyle='--', alpha=0.5)
for bar in bars:
    height = bar.get_height()
    ax_gender.text(bar.get_x() + bar.get_width()/2, height + 20,
                   f'{int(height)} ({height/total_clients*100:.1f}%)', ha='center', va='bottom', fontsize=14, fontweight='bold', color=navy)

# 3. Average Yearly Income
ax_income = fig.add_subplot(gs[0:2, 2])
ax_income.axis('off')
ax_income.add_patch(plt.Rectangle((0.1, 0.1), 0.8, 0.8, fill=True, facecolor='white', alpha=0.9, edgecolor=pink, linewidth=2))
ax_income.text(0.5, 0.7, f"${avg_income:,.0f}", ha='center', va='center', fontsize=36, fontweight='bold', color=pink)
ax_income.text(0.5, 0.3, 'Average Yearly Income', ha='center', va='center', fontsize=14, color='#555', fontweight='medium')

# 4. Average Recency (Age Proxy)
ax_age = fig.add_subplot(gs[0:2, 3])
ax_age.axis('off')
ax_age.add_patch(plt.Rectangle((0.1, 0.1), 0.8, 0.8, fill=True, facecolor='white', alpha=0.9, edgecolor=navy, linewidth=2))
ax_age.text(0.5, 0.7, f"{avg_recency:.0f} days", ha='center', va='center', fontsize=48, fontweight='bold', color=navy)
ax_age.text(0.5, 0.3, 'Average Recency\n(Age Proxy)', ha='center', va='center', fontsize=14, color='#555', fontweight='medium')

# 5. Per Capita Income
ax_per = fig.add_subplot(gs[0:2, 4])
ax_per.axis('off')
ax_per.add_patch(plt.Rectangle((0.1, 0.1), 0.8, 0.8, fill=True, facecolor='white', alpha=0.9, edgecolor=pink, linewidth=2))
ax_per.text(0.5, 0.7, f"${per_capita:,.0f}", ha='center', va='center', fontsize=36, fontweight='bold', color=pink)
ax_per.text(0.5, 0.3, 'Per Capita Income', ha='center', va='center', fontsize=14, color='#555', fontweight='medium')

# 6. Age Group Bar Chart
ax_age_bar = fig.add_subplot(gs[2:4, 2:5])
# Urutkan kolom agar Female dulu jika ada, hindari KeyError
cols = [col for col in ['Female', 'Male'] if col in df['Gender'].unique()]
age_gender = pd.crosstab(df['Age_Group'], df['Gender'])[cols]
age_gender.plot(kind='bar', ax=ax_age_bar, color=[pink, navy][:len(cols)], width=0.8, edgecolor='white', linewidth=1)
ax_age_bar.set_title('Total Clients by Age Group and Gender', fontsize=20, pad=20, fontweight='bold', color=navy)
ax_age_bar.set_xlabel('Age Group', fontsize=14, fontweight='medium')
ax_age_bar.set_ylabel('Number of Clients', fontsize=14, fontweight='medium')
ax_age_bar.legend(title='Gender', fontsize=12, title_fontsize=14)
ax_age_bar.grid(axis='y', linestyle='--', alpha=0.5)
for container in ax_age_bar.containers:
    ax_age_bar.bar_label(container, fmt='%d', fontsize=12, padding=3, fontweight='bold')

# 7. Income Group Pie
ax_income_pie = fig.add_subplot(gs[2, 0:2])
income_vals = df['Income_Group'].value_counts()
max_idx = income_vals.argmax()
explode = [0.1 if i == max_idx else 0.05 for i in range(len(income_vals))]
ax_income_pie.pie(income_vals, labels=income_vals.index,
                  autopct=lambda p: f'{p:.1f}%\n({int(p/100*len(df))})',
                  pctdistance=0.8, colors=pastel_colors, textprops={'fontsize': 12, 'fontweight': 'bold'},
                  explode=explode, shadow=True)
ax_income_pie.set_title('Client Distribution by Income Group', fontsize=18, pad=20, fontweight='bold', color=navy)

# 8. Credit Score Pie
ax_credit_pie = fig.add_subplot(gs[3, 0:2])
credit_vals = df['Credit_Score'].value_counts()
max_idx = credit_vals.argmax()
explode = [0.1 if i == max_idx else 0.05 for i in range(len(credit_vals))]
ax_credit_pie.pie(credit_vals, labels=credit_vals.index,
                  autopct=lambda p: f'{p:.1f}%\n({int(p/100*len(df))})',
                  pctdistance=0.8, colors=set2_colors, textprops={'fontsize': 12, 'fontweight': 'bold'},
                  explode=explode, shadow=True)
ax_credit_pie.set_title('Client Distribution by Credit Score', fontsize=18, pad=20, fontweight='bold', color=navy)

# 9. Risk Category Bar
ax_risk = fig.add_subplot(gs[4, 1:4])
risk_count = df['Risk_Category'].value_counts()
bars = ax_risk.bar(risk_count.index, risk_count.values, color=[green, red], width=0.7, edgecolor='white', linewidth=1)
ax_risk.set_title('Total Clients by Risk Category', fontsize=18, pad=20, fontweight='bold', color=navy)
ax_risk.set_ylabel('Number of Clients', fontsize=14, fontweight='medium')
ax_risk.grid(axis='y', linestyle='--', alpha=0.5)
for bar in bars:
    height = bar.get_height()
    ax_risk.text(bar.get_x() + bar.get_width()/2, height + 20,
                 f'{int(height)} ({height/total_clients*100:.1f}%)', ha='center', fontsize=16, fontweight='bold', color=navy)

# Summary text
high_risk_count = risk_count.get('High Risk', 0)
low_risk_count = risk_count.get('Low Risk', 0)
summary_text = f"""
Key Insights:
- Total Clients: {total_clients:,}
- Gender Ratio: {female_count/total_clients*100:.1f}% Female, {male_count/total_clients*100:.1f}% Male
- Average Income: ${avg_income:,.0f} | Average Recency: {avg_recency:.0f} days
- High Risk Clients: {high_risk_count} ({high_risk_count/total_clients*100:.1f}%)
- Low Risk Clients: {low_risk_count} ({low_risk_count/total_clients*100:.1f}%)
"""
fig.text(0.04, 0.02, summary_text, fontsize=14, color='#34495E', ha='left', va='bottom', fontweight='medium')

# Final layout
plt.tight_layout(rect=[0, 0.05, 1, 0.95])
plt.show()
