import pandas as pd 
import matplotlib.pyplot as plt
import numpy as np
import os
import calendar

target_path = os.path.abspath(os.path.join(os.getcwd(), '..'))
data = os.path.join(target_path, 'Data')
adjusted_csv_path_spl = os.path.join(data, 'final_adjusted_2011_2024.csv')
adjusted_csv_path_bos = os.path.join(data, 'table_mountain_2019_2024_aerosol_data_final.csv')

def GetMonthlyAverages(daily_averages, year, filtered_df, full_data):
    
    """ This function is used to compute monthly averages or bin scattering and absorption
    aerosol data by month. Both are computed from the inputted daily averages dataframe.  
    
    Args:
        - daily_averages (dataframe): dataframe containing daily averaged (julian day) values
        across all years 
        - year (int): starting year
        - filtered_df (dataframe): dataframe containing 
        - full_data (bool): true indicates to compute a boxplot of coefficient data.

    Returns:
        - If full_data variable is True: two tables - a monthly averaged table and 
        a monthly dataframe containing scattering and absorption coefficients to be 
        plotted via boxplot.
        - If full_data variable is False: one table - a monthly averaged table of either
        ssa, sae, or aae variables
    """
        
    
    try:
        
        monthly_avg = []    
        for month in range(1, 13):
            month_name = calendar.month_name[month]
            days_in_month = calendar.monthrange(year, month)[1]
            start = pd.Timestamp(year, month, 1).dayofyear
            end = pd.Timestamp(year, month, days_in_month).dayofyear

            month_data = daily_averages[
                (daily_averages["dayof_year"] >= start) &
                (daily_averages["dayof_year"] <= end)
            ]                
            month_avg = month_data.drop(columns=['dayof_year', 'year', 'Date'], errors='ignore').mean()
            month_avg_dict = month_avg.to_dict()
            month_avg_dict['month'] = month_name 
            monthly_avg.append(month_avg_dict)
        final_df = pd.DataFrame(monthly_avg)

        if not full_data:
            return final_df
        scattering_col = 'pm10_scattering_coeff_550'
        absorption_col = 'pm10_absorption_coeff_550'
        date_col = 'Date'

        tmp = filtered_df[[date_col, scattering_col, absorption_col]].copy()
        tmp[date_col] = pd.to_datetime(tmp[date_col], errors="coerce")
        tmp = tmp.dropna(subset=[date_col, scattering_col, absorption_col])

        tmp["month"] = tmp[date_col].dt.month_name()
        month_order = list(pd.date_range('2000-01-01', periods=12, freq='MS').strftime('%B'))
        tmp["month"] = pd.Categorical(tmp["month"], categories=month_order, ordered=True)
        final_full_df = tmp.drop(columns='Date')
        return final_df, final_full_df
    
    except Exception as e:
        raise ValueError(f"The provided value must be ... (actual error: {e})") from e

# ---------------------------------------------------------------------------------------------------------------------------------

# ---------------------------------------------------------------------------------------------------------------------------------

def ProcessAerosolData(adjusted_csv, selected_columns, variable, region, full_data):
    
    """ This function creates year and data columns that are used to group
    and produce monthly averaged aerosol data based on variable region and 
    boolean conditions. If the variable is ssa, aerosol extinction is compuuted
    and added in a new dataframe.

    Args:
        - adjusted_csv (str): Filepath for either SPL or BOS data
        - selected_columns (list): columns needed for plotting
        - variable (str): variable used to plot: ssa, aae, sae or coeff
        - region (str): SPL or BOS abbreviation
        - full_data (bool): true indicates to compute a boxplot of coefficient data.
    
    Returns:
        - monthly averaged dataframes for the years 2011-2016 and 2024 for SPL
        and the entire BOS data.
        
    """
    
    try:
        monthly_avg_df = None
        full_data_df = None
        final_df = None

        filtered_df = adjusted_csv[selected_columns].dropna(subset=selected_columns).copy()  
        filtered_df['Date'] = pd.to_datetime(filtered_df['Date'], errors='coerce')
        filtered_df['year'] = filtered_df['Date'].dt.year
        filtered_df['dayof_year'] = filtered_df['Date'].dt.day_of_year 
        
        if full_data:
            daily_averages_df = filtered_df.groupby('dayof_year').mean().reset_index()
            monthly_avg_df, full_data_df = GetMonthlyAverages(daily_averages_df, 2011, filtered_df, full_data)
            
        else:
            if variable == "ssa":
                ssa_df = filtered_df[['Date', 'year', 'dayof_year']].copy()
                pm = "pm10"
                scat_col = f"{pm}_scattering_coeff_550"
                abs_col  = f"{pm}_absorption_coeff_550"
                total = filtered_df[scat_col] + filtered_df[abs_col]
                with np.errstate(divide="ignore", invalid="ignore"):
                    ssa_df[f"{pm}_ssa_550"] = np.where(total != 0,
                                                            filtered_df[scat_col] / total,
                                                            np.nan)
                filtered_df = ssa_df
            if region == "SPL":
                filtered_df_2011_2024 = filtered_df[filtered_df['year'].between(2011, 2024)].copy()
                filtered_df_2011_2016 = filtered_df[filtered_df['year'].between(2011, 2016)].copy()
                
                filtered_df_2011_2024 = filtered_df_2011_2024.drop(columns=["year", "Date"], errors="ignore")
                filtered_df_2011_2016 = filtered_df_2011_2016.drop(columns=["year", "Date"], errors="ignore") 
                
                filtered_df_2011_2024.rename(columns={column: f'{column}_2024' for column in filtered_df_2011_2024.columns if column != 'dayof_year'}, inplace=True)
                filtered_df_2011_2016.rename(columns={column: f'{column}_2016' for column in filtered_df_2011_2016.columns if column != 'dayof_year'}, inplace=True)

                daily_average_2011_2024 = filtered_df_2011_2024.groupby('dayof_year').mean().reset_index() 
                daily_average_2011_2016 = filtered_df_2011_2016.groupby('dayof_year').mean().reset_index() 

                monthly_averages_2016 = GetMonthlyAverages(daily_average_2011_2016, 2011, None, False)
                monthly_averages_2024 = GetMonthlyAverages(daily_average_2011_2024, 2011, None, False)
                
                final_df = monthly_averages_2016.merge(monthly_averages_2024, on='month')        
            elif region == "BOS":
                filtered_df = filtered_df.drop(columns=["year", "Date"], errors="ignore") 
                filtered_df.rename(columns={column: f'{column}_bos' for column in filtered_df.columns if column != 'dayof_year'}, inplace=True)
                daily_averages_bos = filtered_df.groupby('dayof_year').mean().reset_index() 
                final_df = GetMonthlyAverages(daily_averages_bos, 2011, None, False)       
            else:
                raise ValueError("region must be 'SPL' or 'BOS'")
        return final_df, monthly_avg_df, full_data_df
    except Exception as e:
        raise 
    
# ---------------------------------------------------------------------------------------------------------------------------------

# ---------------------------------------------------------------------------------------------------------------------------------

def plot_full_data(full_data_df_spl, full_data_df_bos, monthly_avg_df_spl, monthly_avg_df_bos):
    
    """ This function contains the code logic to plot side-by-side 
    boxplots of aerosol scattering and absorption coefficients for both SPL and BOS

    Args:
        - full_data_df_spl (dataframe): datafrane containing binned monthly
        aerosol scattering and absorption data for SPL
        - full_data_df_bos (dataframe): datafrane containing binned monthly
        aerosol scattering and absorption data for BOS
        - monthly_avg_df_spl (dataframe): datafrane containing monthly 
        averaged data for scattering and absorption for SPL
        - monthly_avg_df_bos (dataframe): datafrane containing monthly 
        averaged data for scattering and absorption for BOS
        
    Returns:
        - None
        
    """
    
    try:
        scattering_col = "pm10_scattering_coeff_550"
        absorption_col = "pm10_absorption_coeff_550"

        fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(12, 10), gridspec_kw={'wspace': 0.3})

        months_spl = list(monthly_avg_df_spl["month"].unique())
        months_bos = list(monthly_avg_df_bos["month"].unique())

        def full_box_with_monthly_line(ax, full_df, monthly_df, col, months, facecolor, line_color):
            box_data = [
                full_df.loc[full_df["month"] == m, col].dropna()
                for m in months
            ]
            ax.boxplot(
                box_data,
                tick_labels=months,
                patch_artist=True,
                boxprops=dict(facecolor=facecolor),
                showfliers=False,
                medianprops={"color": "black", "linewidth": 1.5},
            )

            means = [
                monthly_df.loc[monthly_df["month"] == m, col].dropna().mean()
                for m in months
            ]
            ax.plot(
                np.arange(len(months)) + 1,
                means,
                color=line_color,
                marker="o",
                markerfacecolor='white',
                markeredgecolor='black',
                markersize=8,
                linewidth=2,
                zorder=3,
            )

        full_box_with_monthly_line(ax1, full_data_df_spl, monthly_avg_df_spl, scattering_col, months_spl, "orange", "black")
        full_box_with_monthly_line(ax2, full_data_df_bos, monthly_avg_df_bos, scattering_col, months_bos, "steelblue", "black")
        full_box_with_monthly_line(ax3, full_data_df_spl, monthly_avg_df_spl, absorption_col, months_spl, "orange", "black")
        full_box_with_monthly_line(ax4, full_data_df_bos, monthly_avg_df_bos, absorption_col, months_bos, "steelblue", "black")

        ax1.set_ylabel("σ$_s$$_p$ (550 nm, Mm$^-$$^1$)\n", fontsize=16)
        ax1.set_title("SPL", fontweight="bold", fontsize=30, pad=40)
        ax1.tick_params(axis="both", which="major", labelsize=14, width=1, length=12, pad=20)
        ax1.tick_params(axis="x", top=True, labeltop=False, labelbottom=False)
        ax1.tick_params(axis="y", right=True, labelright=False)
        ax1.grid(axis="both", linestyle="--", alpha=0.5)

        ax2.set_title("BOS", fontweight="bold", fontsize=30, pad=40)
        ax2.tick_params(axis="both", which="major", labelsize=14, width=1, length=12, pad=20)
        ax2.tick_params(axis="x", top=True, labeltop=False, labelbottom=False)
        ax2.tick_params(axis="y", right=True, labelright=False)
        ax2.grid(axis="both", linestyle="--", alpha=0.5)

        ax3.set_ylabel("σ$_a$$_p$ (550 nm, Mm$^-$$^1$)\n", fontsize=16)
        ax3.tick_params(axis="both", which="major", labelsize=14, width=1, length=12, pad=20)
        ax3.tick_params(axis="x", top=True, labeltop=False)
        ax3.tick_params(axis="y", right=True, labelright=False)
        ax3.grid(axis="both", linestyle="--", alpha=0.5)
        ax3.set_xticklabels(['J', 'F', 'M', 'A', 'M', 'J', 'J', 'A', 'S', 'O', 'N', 'D'], fontsize=16)


        ax4.tick_params(axis="both", which="major", labelsize=14, width=1, length=12, pad=20)
        ax4.tick_params(axis="x", top=True, labeltop=False)
        ax4.tick_params(axis="y", right=True, labelright=False)
        ax4.grid(axis="both", linestyle="--", alpha=0.5)
        ax4.set_xticklabels(['J', 'F', 'M', 'A', 'M', 'J', 'J', 'A', 'S', 'O', 'N', 'D'], fontsize=16)

        plt.show()
        return
    
    except Exception as e:
        raise e

# ---------------------------------------------------------------------------------------------------------------------------------

# ---------------------------------------------------------------------------------------------------------------------------------

def GetAerosolVariableData(optical, variable, full_data):
    
    """ This function is used to plot different aerosol plots for both 
    BOS and SPL based on the coefficient, variable and boolean condition provided.

    Args:
        - optical (str): either scattering or absorption coefficient
        - variable (str): variable used to plot: ssa, aae, sae or coeff
        - full_data (bool): true indicates to compute a boxplot of coefficient data.
    
    Returns:
        - None
    """
    
    try:
        if variable == "angstrom":
            variables = [
                "pm10_scattering_angstrom_450_700", 
                "pm10_absorption_angstrom_450_700"
            ]
            selected_variable_columns_spl = [
            'month',
            f'pm10_{optical}_{variable}_450_700_2024',
            f'pm10_{optical}_{variable}_450_700_2016',
            ]
            
            selected_variable_columns_bos = [
                'month', 
                f'pm10_{optical}_{variable}_450_700_bos'
            ]
        
        elif variable == "ssa" or variable == "full_data":
            variables = [
                "pm10_scattering_coeff_550", 
                "pm10_absorption_coeff_550"
            ]
            selected_variable_columns_spl = [
                'month',
                f'pm10_{variable}_550_2024',
                f'pm10_{variable}_550_2016'
            ]
            selected_variable_columns_bos = [
                'month',
                f'pm10_{variable}_550_bos',
            ]
        elif variable == 'coeff':
            variables = [
                "pm10_scattering_coeff_550", 
                "pm10_absorption_coeff_550"
            ]
        else:
            pass
        
        for file in [adjusted_csv_path_spl, adjusted_csv_path_bos]:
            adjusted_csv = pd.read_csv(file, header=0) 
            adjusted_csv.replace([99999.99, 9999.99, 999.999999, 
                999.999, 999.99, 99.999, 9.999], np.nan, inplace=True) 
            file_basename = os.path.basename(file)

            if file_basename.startswith('final'):
                adjusted_csv_spl = adjusted_csv
                selected_columns_spl = [columns for columns in adjusted_csv_spl.columns
                            if columns == "Date" or columns in variables]
            elif file_basename.startswith('table'):
                adjusted_csv_bos = adjusted_csv
                selected_columns_bos = [columns for columns in adjusted_csv_bos.columns
                            if columns == "Date" or columns in variables]
            else:
                continue
        
        spl_data, monthly_avg_df_spl, full_data_df_spl = ProcessAerosolData(adjusted_csv_spl, selected_columns_spl, variable, 'SPL', full_data)
        bos_data, monthly_avg_df_bos, full_data_df_bos = ProcessAerosolData(adjusted_csv_bos, selected_columns_bos, variable, 'BOS', full_data)
        
        if full_data:
            plot_full_data(full_data_df_spl, full_data_df_bos, monthly_avg_df_spl, monthly_avg_df_bos)

        else:
            spl_data = spl_data[selected_variable_columns_spl]
            bos_data = bos_data[selected_variable_columns_bos]
            merged_data = bos_data.merge(spl_data, on='month')
        
            if variable == 'ssa':
                var_label = 'PM$_1$$_0$ SSA (450 & 700 nm)' 
            elif variable == 'angstrom':
                if optical == 'scattering':
                    var_label = 'PM$_1$$_0$ SAE (450 & 700 nm)'
                elif optical == 'absorption':
                    var_label = 'PM$_1$$_0$ AAE (450 & 700 nm)'

            else:
                pass
                
            key = ['BOS 2019-2024', 'SPL 2011-2016', 'SPL 2011-2024']
            plt.figure(figsize=(12,6))
            for col in merged_data.columns:
                if col.endswith('bos'):
                    plt.plot(merged_data['month'], merged_data[col], label=key[0], marker='d', color='orange')
                elif col.endswith('2016'):
                    plt.plot(merged_data['month'], merged_data[col], label=key[1], marker='d', color='green')
                elif col.endswith('2024'):
                    plt.plot(merged_data['month'], merged_data[col], label=key[2], marker='d', linestyle='dashed', color='blue')
            plt.legend(loc='upper left', frameon=False, fontsize=10)
            plt.ylabel(f'{var_label}', fontsize=14, labelpad=20)
            plt.grid(alpha=0.5, linestyle='--')
            plt.gca().set_xticklabels(['J','F','M','A','M','J','J','A','S','O','N','D'], fontsize=16)
            plt.tick_params(axis='both', which='major', labelsize=14, width=1, length=12, pad=20)
            plt.tick_params(axis='x', top=True, labeltop=False)
            plt.tick_params(axis='y', right=True, labelright=False)
            plt.show()
            plt.close()
    
    except Exception as e:
        raise e