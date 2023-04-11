# plotting graphs
import os
try:
    from FreeCAD.Plot import Plot
except ImportError:
    from freecad.plot import Plot
from matplotlib.transforms import Bbox


fig = Plot.figure(winTitle = "Topology Optimization")
plt = Plot.getPlot()
rect = plt.axes.get_position().get_points()
rect[0][0] = rect[1][0]/1.7
rect[0][1] = rect[1][1]/1.7
bbox = Bbox(rect)
Plot.addNewAxes(rect =bbox)
axes = Plot.axesList()

def replot(path, i, oscillations, mass, domain_FI_filled, domains_from_config, FI_violated, FI_mean, FI_mean_without_state0,
           FI_max, optimization_base, energy_density_mean, heat_flux_mean, displacement_graph, disp_max,
           buckling_factors_all,savefig=False):

    ax = axes[0]
    ax.cla()
    ax.plot(range(i+1), mass, label="Mass",color ="red")
    ax.grid()
    ax.set_xlabel("Iteration")
    ax.set_ylabel("Mass")
    # plt.pause(0.0001)
    fig.canvas.flush_events()
    if savefig:
        Plot.save(os.path.join(path, "Mass"))

    if oscillations is True:
        i_plot = i - 1  # because other values for i-th iteration are not evaluated
    else:
        i_plot = i

    if domain_FI_filled:  # FI contain something
        # plot number of elements with FI > 1
        dno = 0
        for dn in domains_from_config:
            FI_violated_dn = []
            for ii in range(i_plot + 1):
                FI_violated_dn.append(FI_violated[ii][dno])
            ax = axes[1]
            ax.cla()
            ax.set_xlabel("Iteration")
            ax.set_ylabel("FI_violated")
            ax.plot(range(i_plot + 1), FI_violated_dn, label=dn,color ="orange")
            ax.patch.set_alpha(0.01)
            dno += 1
        if len(domains_from_config) > 1:
            FI_violated_total = []
            for ii in range(i_plot + 1):
                FI_violated_total.append(sum(FI_violated[ii]))
            ax.plot(range(i_plot+1), FI_violated_total, label="Total",color ="orange")
        # plt.pause(0.0001)
        fig.canvas.flush_events()
        if savefig:
            Plot.save(os.path.join(path, "FI_violated"))

        ax.plot(range(i_plot+1), FI_mean, label="all")
        ax.plot(range(i_plot+1), FI_mean_without_state0, label="without state 0")
        Plot.title("Mean Failure Index weighted by element mass")
        Plot.xlabel("Iteration")
        Plot.ylabel("FI_mean")
        Plot.legend(loc=2, fontsize=10)
        # plt.pause(0.0001)
        fig.canvas.flush_events()
        if savefig:
            Plot.save(os.path.join(path, "FI_mean"))

        # plot maximal failure indices
        for dn in domains_from_config:
            FI_max_dn = []
            for ii in range(i_plot + 1):
                FI_max_dn.append(FI_max[ii][dn])
            plt.setActiveAxes(1)
            """seriesList_2 = Plot.series()
            if len(seriesList_2) > 1:
                Plot.removeSerie(0)"""
            ax.plot(range(i_plot + 1), FI_max_dn, label=dn)
        Plot.legend(loc=2, fontsize=10)
        Plot.title("Maximal domain Failure Index")
        Plot.xlabel("Iteration")
        Plot.ylabel("FI_max")
        # plt.pause(0.0001)
        fig.canvas.flush_events()
        if savefig:
            Plot.save(os.path.join(path, "FI_max"))

    if optimization_base == "stiffness":
        # plot mean energy density
        ax = axes[1]
        ax.cla()
        ax.set_xlabel("Iteration")
        ax.set_ylabel("Energy Density Mean")
        ax.plot(range(i_plot+1), energy_density_mean,label ="energy density",color = "orange")
        ax.patch.set_alpha(0.01)
        fig.canvas.flush_events()
        # plt.pause(0.0001)
        if savefig:
            Plot.save(os.path.join(path, "energy_density_mean"))

    if optimization_base == "heat":
        # plot mean heat flux
        ax = axes[1]
        ax.cla()
        ax.set_xlabel("Iteration")
        ax.set_ylabel("Heat Flux Mean")
        ax.plot(range(i_plot+1), heat_flux_mean,color = "orange")
        ax.patch.set_alpha(0.01)
        # plt.pause(0.0001)
        fig.canvas.flush_events()
        if savefig:
            Plot.save(os.path.join(path, "heat_flux_mean"))

    if displacement_graph:
        ax = axes[1]
        ax.cla()
        ax.set_xlabel("Iteration")
        ax.set_ylabel("Displacement")
        for cn in range(len(displacement_graph)):
            disp_max_cn = []
            for ii in range(i_plot + 1):
                disp_max_cn.append(disp_max[ii][cn])
            ax.plot(range(i + 1), disp_max_cn, label=displacement_graph[cn][0] + "(" + displacement_graph[cn][1] + ")",color ="orange")
        ax.patch.set_alpha(0.01)
        fig.canvas.flush_events()
        if savefig:
            Plot.save(os.path.join(path, "Displacement_max"))

    if optimization_base == "buckling":
        ax = axes[1]
        ax.cla()
        ax.set_xlabel("Iteration")
        ax.set_ylabel("Buckling Factors")
        for bfn in range(len(buckling_factors_all[0])):
            buckling_factors_bfn = []
            for ii in range(i_plot + 1):
                buckling_factors_bfn.append(buckling_factors_all[ii][bfn])
            ax.plot(range(i_plot + 1), buckling_factors_bfn, label="mode " + str(bfn + 1))
        ax.patch.set_alpha(0.01)
        # plt.pause(0.0001)
        fig.canvas.flush_events()
        if savefig:
            Plot.save(os.path.join(path, "buckling_factors"))
