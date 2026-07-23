
import math
import streamlit as st
import pandas as pd

st.set_page_config(page_title="Capacitor Calculator", page_icon="⚡", layout="wide")

E12_BASE=[1.0,1.2,1.5,1.8,2.2,2.7,3.3,3.9,4.7,5.6,6.8,8.2]
DECADES=[1,10,100]

def add_capacitor(values,c): values.append(c)

def build_one_decade(values,m):
    for n in E12_BASE:
        add_capacitor(values,n*m)

def build_pf_values(values):
    for d in DECADES: build_one_decade(values,d)

def build_nf_values(values):
    for d in DECADES: build_one_decade(values,d*1000)

def build_uf_values(values):
    for d in DECADES: build_one_decade(values,d*1000000)

def remove_duplicates(values):
    out=[]
    for v in values:
        if v not in out: out.append(v)
    return out

def sort_values(values):
    values.sort()
    return values

def build_standard_capacitors():
    lst=[]
    build_pf_values(lst)
    build_nf_values(lst)
    build_uf_values(lst)
    return sort_values(remove_duplicates(lst))

STANDARD_CAPS_pF=build_standard_capacitors()

def convert_frequency_to_hz(v,u):
    u=u.lower()
    return {"hz":v,"khz":v*1000,"mhz":v*1000000}[u]

def calculate_difference(a,b): return abs(a-b)

def find_nearest_standard(calc):
    nearest=STANDARD_CAPS_pF[0]
    smallest=calculate_difference(calc,nearest)
    for c in STANDARD_CAPS_pF:
        d=calculate_difference(calc,c)
        if d<smallest:
            smallest=d
            nearest=c
    return nearest

def calculate_capacitance_farads(f,r):
    return 1/(2*math.pi*f*r)

def convert_farads_to_pf(f): return f*1e12

def calculate_capacitor(f,r):
    pf=convert_farads_to_pf(calculate_capacitance_farads(f,r))
    return pf,find_nearest_standard(pf)

def format_capacitance(v):
    if v>=1e6: return f"{v/1e6:.4f} µF"
    elif v>=1000: return f"{v/1000:.4f} nF"
    return f"{v:.4f} pF"

def get_initial_resistor(op):
    op=op.upper()
    if op=="BJT": return 1000
    return 10000

def calculate_final_resistor(f,stdpf):
    return 1/(2*math.pi*f*(stdpf*1e-12))

def format_resistance(r):
    if r>=1e6: return f"{r/1e6:.3f} MΩ"
    elif r>=1e3: return f"{r/1e3:.3f} kΩ"
    return f"{r:.3f} Ω"

st.title("⚡ Capacitor Calculator")
st.caption("C = 1 / (2 × π × Frequency × Resistance)")

left,right=st.columns([1,1])

with left:
    st.subheader("Inputs")
    op=st.selectbox("Op Amp Type",["BJT","FET","CMOS"])
    freq_text=st.text_input("Frequency Value","100")
    unit=st.selectbox("Frequency Unit",["Hz","kHz","MHz"])
    calc=st.button("Calculate",use_container_width=True)

with right:
    st.subheader("Results")

    if calc:
        try:
            fval=float(freq_text)
            fhz=convert_frequency_to_hz(fval,unit)
            initial=get_initial_resistor(op)
            calc_pf,std_pf=calculate_capacitor(fhz,initial)
            final_r=calculate_final_resistor(fhz,std_pf)

            c1,c2=st.columns(2)
            c1.metric("Initial Resistor",format_resistance(initial))
            c2.metric("Final Resistor",format_resistance(final_r))

            c3,c4=st.columns(2)
            c3.metric("Calculated Capacitor",format_capacitance(calc_pf))
            c4.metric("Nearest Standard",format_capacitance(std_pf))

        except Exception:
            st.error("Please enter a valid frequency.")

with st.expander("Standard Capacitor Database"):
    df=pd.DataFrame({"Capacitor (pF)":STANDARD_CAPS_pF})
    st.dataframe(df,use_container_width=True,height=400)
