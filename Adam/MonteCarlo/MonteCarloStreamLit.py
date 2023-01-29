#Code to Incorportate in 'my_app.py'

#List of parameters that will be entered into the Monte Carlo Simulations
Monte_Carlo__list=[get_MC_input(api_call_df, four_portfolios_df, portfolio, initial_investment, time_horizon) for portfolio in four_portfolios]

#Inserting a blank index on the portfolios list to enhance runtime
four_portfolios.insert(0,'')

with tab4:

    #Formatting the Webpage for the Monte Carlo Portion
    st.header("Future Predictions of Portfolios:")

    st.subheader("Monte Carlo Simulation Analysis:")

    st.write(f"**With the utilization of a simulation known as 'Monte Carlo', your portfolios were analyzed for their estimated future returns using an intial invesment of :blue[${initial_investment:.2f}] over the span of :blue[{time_horizon:.0f}] years.**")

    st.write("**The following were the outcomes...**")

    st.caption("_**Disclaimer:** These results are not guaranteed but rather an estimate based on the assumption of normal distribution, which quantifies risk and return by the mean for returns and standard deviation for risk. Outcome is based on random number algorithm and may not render consistent results._")

    st.header(f"{time_horizon:.0f} Year Portfolio Analysis:")

    monte_selection = st.selectbox("Select the portfolio for analysis:", four_portfolios)


    #An if/else statement for each of the portfolios which will run that specific Monte Carlo Simulation if the portfolio is chosen by the user.
    if monte_selection == four_portfolios[1]:

        #Spinner for viewer to see whilst Monte Carlo Sim is loading
        with st.spinner('Wait for it...'):
            time.sleep(7)
            st.success('Done!')

        #Calling Monte Carlo Sim on Capacity Portfolio
        Capacity_MC = MCSimulation(
        portfolio_data = Monte_Carlo__list[0][0],
        investment_amount = Monte_Carlo__list[0][2],
        weights = Monte_Carlo__list[0][1],
        num_simulation = 100, 
        years = int(Monte_Carlo__list[0][3]))

        #Getting HvPlots and Returns on Capacity Sim
        capacity_plot = Capacity_MC.plot_simulation()
        capacity_dist = Capacity_MC.plot_distribution()
        capacity_returns = Capacity_MC.return_amount()

        st.subheader("**Capacity Portfolio:**")

        column1, column2, column3 = st.columns(3, gap='large')

        with column1:

            st.markdown("**Monte Carlo Plot based on 100 Simulations**:")

            st.bokeh_chart(hv.render(capacity_plot, backend='bokeh'), use_container_width=True)

        with column2:

            st.markdown("**Distribution of 100 Simulations:**")

            st.bokeh_chart(hv.render(capacity_dist, backend='bokeh'), use_container_width=True)

        with column3:

            st.header('\n')
            st.header('\n')

            st.subheader(f'With a 95% confidence, an initial investment of _${initial_investment}_ over the course of _{time_horizon} years_ will result in your capacity portfolio having an estimated return value between **:blue[{capacity_returns[0]:.2f}]** and **:blue[{capacity_returns[1]:.2f}]** USD.')

    elif monte_selection == four_portfolios[2]:

        #Spinner for viewer to see whilst Monte Carlo Sim is loading
        with st.spinner('Wait for it...'):
            time.sleep(7)
            st.success('Done!')

        #Calling Monte Carlo Sim on Tolerance Portfolio
        Tolerance_MC = MCSimulation(
        portfolio_data = Monte_Carlo__list[1][0],
        investment_amount = Monte_Carlo__list[1][2],
        weights = Monte_Carlo__list[1][1],
        num_simulation = 100, 
        years = int(Monte_Carlo__list[1][3]))

        #Getting HvPlots and Returns on Capacity Sim
        tolerance_plot = Tolerance_MC.plot_simulation()
        tolerance_dist = Tolerance_MC.plot_distribution()
        tolerance_returns = Tolerance_MC.return_amount()

        st.subheader("**Tolerance Portfolio:**")

        column1, column2, column3 = st.columns(3, gap='large')

        with column1:

            st.markdown("**Monte Carlo Plot based on 100 Simulations:**")

            st.bokeh_chart(hv.render(tolerance_plot, backend='bokeh'), use_container_width=True)

        with column2:

            st.markdown("**Distribution of 100 Simulations:**")

            st.bokeh_chart(hv.render(tolerance_dist, backend='bokeh'), use_container_width=True)

        with column3:

            st.header('\n')
            st.header('\n')

            st.subheader(f'With a 95% confidence, an initial investment of _${initial_investment}_ over the course of _{time_horizon} years_ will result in your capacity portfolio having an estimated return value between **:blue[{tolerance_returns[0]:.2f}]** and **:blue[{tolerance_returns[1]:.2f}]** USD.')

    elif monte_selection == four_portfolios[3]:

        #Spinner for viewer to see whilst Monte Carlo Sim is loading
        with st.spinner('Wait for it...'):
            time.sleep(7)
            st.success('Done!')

        #Calling Monte Carlo Sim on Benchmark Portfolio
        Benchmark_MC = MCSimulation(
        portfolio_data = Monte_Carlo__list[2][0],
        investment_amount = Monte_Carlo__list[2][2],
        weights = Monte_Carlo__list[2][1],
        num_simulation = 100, 
        years = int(Monte_Carlo__list[2][3]))

        #Getting HvPlots and Returns on Benchmark Sim
        benchmark_plot = Benchmark_MC.plot_simulation()
        benchmark_dist = Benchmark_MC.plot_distribution()
        benchmark_returns = Benchmark_MC.return_amount()

        st.subheader("**Benchmark Portfolio:**")

        column1, column2, column3 = st.columns(3, gap='large')

        with column1:

            st.markdown("**Monte Carlo Plot based on 100 Simulations:**")

            st.bokeh_chart(hv.render(benchmark_plot, backend='bokeh'), use_container_width=True)

        with column2:

            st.markdown("**Distribution of 100 Simulations:**")

            st.bokeh_chart(hv.render(benchmark_dist, backend='bokeh'), use_container_width=True)

        with column3:

            st.header('\n')
            st.header('\n')

            st.subheader(f'With a 95% confidence, an initial investment of _${initial_investment}_ over the course of _{time_horizon} years_ will result in your capacity portfolio having an estimated return value between **:blue[{benchmark_returns[0]:.2f}]** and **:blue[{benchmark_returns[1]:.2f}]** USD.')

    elif monte_selection == four_portfolios[4]:

        #Spinner for viewer to see whilst Monte Carlo Sim is loading
        with st.spinner('Wait for it...'):
            time.sleep(7)
            st.success('Done!')

        #Calling Monte Carlo Sim on Cryptomix Portfolio
        Cryptomix_MC = MCSimulation(
        portfolio_data = Monte_Carlo__list[3][0],
        investment_amount = Monte_Carlo__list[3][2],
        weights = Monte_Carlo__list[3][1],
        num_simulation = 100, 
        years = int(Monte_Carlo__list[3][3]))

        cryptomix_plot = Cryptomix_MC.plot_simulation()
        cryptomix_dist = Cryptomix_MC.plot_distribution()
        cryptomix_returns = Cryptomix_MC.return_amount()

        st.subheader("**Cryptomix Portfolio:**")

        column1, column2, column3 = st.columns(3, gap='large')

        with column1:

            st.markdown("**Monte Carlo Plot based on 100 Simulations:**")

            st.bokeh_chart(hv.render(cryptomix_plot, backend='bokeh'), use_container_width=True)

        with column2:

            st.markdown("**Distribution of 100 Simulations:**")

            st.bokeh_chart(hv.render(cryptomix_dist, backend='bokeh'), use_container_width=True)

        with column3:

            st.header('\n')
            st.header('\n')

            st.subheader(f'With a 95% confidence, an initial investment of _${initial_investment}_ over the course of _{time_horizon} years_ will result in your capacity portfolio having an estimated return value between **:blue[{cryptomix_returns[0]:.2f}]** and **:blue[{cryptomix_returns[1]:.2f}]** USD.')
