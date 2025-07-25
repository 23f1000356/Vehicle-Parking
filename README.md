# Vehicle Parking Management System

## Project Overview

The aim of this project is to create a Vehicle Parking Management System that helps users book parking spots at various locations. It is a multi-user application with distinct roles for Administrators and Regular Users. The system provides real-time parking spot availability and management capabilities.

## Core Features

### User Management
- Multiple regular users and one admin role
- Secure user authentication and profile management
- Personalized dashboards for both admin and users

### Parking Management
- Admin can create and manage multiple parking lots
- Each parking lot can have multiple parking spots
- Dynamic pricing based on location
- Real-time tracking of spot availability

### Booking System
- Users can book parking spots at various locations
- Support for different vehicle types (Car, Truck, Bike, Scooty, Cycle)
- Duration-based booking system
- Automatic cost calculation based on duration and location

### Search and Filter
- Advanced search functionality based on:
  - Parking lot location
  - Vehicle type
  - User ID
  - Address

### Analytics and Reporting
- Comprehensive summary dashboard showing:
  - Real-time parking spot availability
  - Revenue generation by location
  - Peak hour analysis
  - Vehicle type distribution
  - Total bookings and occupancy rates

### Additional Features
- Automatic spot assignment
- Active reservation tracking
- Booking history
- Contact and support system
- User-friendly interface for spot booking and management

## Technical Implementation

The system is built using:
- Flask web framework
- SQLite database
- SQLAlchemy ORM
- Secure password hashing with bcrypt
- Interactive charts and analytics
- Responsive web design

## Key Entities

1. **Users**
   - Regular users who can book parking spots
   - Admin who manages the parking system

2. **Parking Lots**
   - Multiple locations
   - Configurable number of spots
   - Location-specific pricing

3. **Parking Spots**
   - Individual parking spaces
   - Real-time availability status
   - Linked to specific parking lots

4. **Reservations**
   - Booking details
   - Vehicle information
   - Duration and cost tracking
   - Booking status management

This system provides an efficient solution for managing vehicle parking in multiple locations while offering a user-friendly interface for both administrators and regular users. The real-time availability tracking and comprehensive analytics make it a powerful tool for parking management.
