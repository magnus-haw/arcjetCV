# Introduction

Arcjet Computer Vision (```arcjetCV```) is a software application built to automate analysis of arc jet ground test video footage. This includes tracking material recession, sting arm motion, and the shock-material standoff distance. Consequently, ArcjetCV provides a new capability to resolve and validate new physics associated with non-linear processes. This is an essential step to reduce testing, modeling, and validation uncertainties for heatshield material performance.

Arc jets are plasma wind tunnels used to test the performance of heatshield materials for spacecraft atmospheric entry. These facilities present an extremely harsh flow environment with heat fluxes up to 109 W/$m^2$ for up to 30 minutes. The plasma is low-temperature ($\sim1$ eV) but high pressure ($>$ 10 kPa) creating high-enthalpy supersonic flows similar to atmospheric entry conditions. Typically, material samples are measured before and after a test to characterize the total recession. However, this does not capture time-dependent effects such as material expansion and non-linear recession.

Since manual segmentation is onerous, very few time-resolved measurements of material recession/expansion/shrinkage under arcjet test conditions exist. ArcjetCV seeks to automate these measurements such that time-resolved material behavior can be extracted for every arc jet test.

ArcjetCV makes new time-resolved measurements of material recession, expansion new analysis of arcjet test videos which measure both the time-dependent 2D recession of the material samples and the shock standoff distance. The results show non-linear time-dependent effects are present for some conditions. The material and shock edges are extracted from the videos by training and applying a convolutional neural network. Due to the consistent camera settings, the machine learning model achieves high accuracy ($\pm$ 2 px) relative to manually segmented images with only a small number of training frames.