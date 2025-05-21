import matplotlib.pyplot as plt
import numpy as np
import streamlit as st
from sklearn.preprocessing import PolynomialFeatures
from sklearn.linear_model import LinearRegression
from sklearn.pipeline import make_pipeline
from sklearn.metrics import r2_score

def str2int(range_str):
    # Pisahkan string berdasarkan tanda "-"
    start, end = map(int, range_str.split('-'))

    # Hitung rata-rata
    average = (start + end) / 200
    return average,start,end

def polynomial_regression(netOD, dosis_aktual, degree=3, plot=True):
    # Konversi ke numpy array
    X = np.array(netOD).reshape(-1, 1)
    y = np.array(dosis_aktual)

    # Transformasi fitur polinomial
    poly = PolynomialFeatures(degree)
    X_poly = poly.fit_transform(X)

    # Fit model regresi
    model = LinearRegression()
    model.fit(X_poly, y)
    coeff = [model.intercept_] + list(model.coef_[1:])  # Abaikan coef_[0] karena itu untuk x^0

    # Plot jika diminta
    if plot:
        X_range = np.linspace(min(netOD), max(netOD), 300).reshape(-1, 1)
        X_range_poly = poly.transform(X_range)
        y_pred_plot = model.predict(X_range_poly)

        # Hitung R²
        y_pred_r2 = model.predict(X_poly)
        r2 = r2_score(y, y_pred_r2)

        # Bentuk persamaan dalam format string
        equation_terms = [f"{coeff[0]:.2f}"]
        for i in range(1, len(coeff)):
            term = f"{coeff[i]:+.2f}x"
            if i > 1:
                term += f"^{i}"
            equation_terms.append(term)
        equation_str = "y = " + " ".join(equation_terms)

        # Plot data dan kurva
        plt.figure(figsize=(8, 5))
        plt.scatter(netOD, dosis_aktual, color='blue', label='Data Asli')
        plt.plot(X_range, y_pred_plot, color='red', label=f'Polinom degree={degree}')
        plt.xlabel('netOD')
        plt.ylabel('Dosis Aktual (cGy)')
        plt.title('Regresi Polinomial antara netOD dan Dosis Aktual')
        plt.grid(True)
        plt.legend()

        # Tambahkan teks persamaan dan R² ke dalam plot
        plt.text(max(X_range)*0.4, max(dosis_aktual)*0.08, f"${equation_str}$", fontsize=10, color='darkgreen')
        plt.text(max(X_range)*0.8, max(dosis_aktual)*0.01, f"$R^2$ = {r2:.4f}", fontsize=10, color='purple')

        plt.tight_layout()
        plt.show()
        st.pyplot(plt)
    return lambda x:coeff[0]+coeff[1]*x+coeff[2]*x**2+coeff[3]*x**3