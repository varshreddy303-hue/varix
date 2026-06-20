-- Enable RLS on tables that don't have it
ALTER TABLE permissions ENABLE ROW LEVEL SECURITY;
ALTER TABLE role_permissions ENABLE ROW LEVEL SECURITY;
ALTER TABLE user_roles ENABLE ROW LEVEL SECURITY;

-- Global permissions table: read-only for authenticated users
CREATE POLICY "select_permissions" ON permissions FOR SELECT TO authenticated USING (true);

-- Global roles table: managed by admins, scoped to organization
CREATE POLICY "select_roles" ON roles FOR SELECT TO authenticated USING (organization_id = (auth.jwt() ->> 'org_id')::uuid);
CREATE POLICY "insert_roles" ON roles FOR INSERT TO authenticated WITH CHECK (organization_id = (auth.jwt() ->> 'org_id')::uuid);
CREATE POLICY "update_roles" ON roles FOR UPDATE TO authenticated USING (organization_id = (auth.jwt() ->> 'org_id')::uuid) WITH CHECK (organization_id = (auth.jwt() ->> 'org_id')::uuid);
CREATE POLICY "delete_roles" ON roles FOR DELETE TO authenticated USING (organization_id = (auth.jwt() ->> 'org_id')::uuid);

-- Role permissions junction table
CREATE POLICY "select_role_permissions" ON role_permissions FOR SELECT TO authenticated USING (
  EXISTS (SELECT 1 FROM roles WHERE roles.id = role_permissions.role_id AND roles.organization_id = (auth.jwt() ->> 'org_id')::uuid)
);
CREATE POLICY "insert_role_permissions" ON role_permissions FOR INSERT TO authenticated WITH CHECK (
  EXISTS (SELECT 1 FROM roles WHERE roles.id = role_permissions.role_id AND roles.organization_id = (auth.jwt() ->> 'org_id')::uuid)
);
CREATE POLICY "delete_role_permissions" ON role_permissions FOR DELETE TO authenticated USING (
  EXISTS (SELECT 1 FROM roles WHERE roles.id = role_permissions.role_id AND roles.organization_id = (auth.jwt() ->> 'org_id')::uuid)
);

-- User roles junction table
CREATE POLICY "select_user_roles" ON user_roles FOR SELECT TO authenticated USING (
  EXISTS (SELECT 1 FROM users WHERE users.id = user_roles.user_id AND users.organization_id = (auth.jwt() ->> 'org_id')::uuid)
);
CREATE POLICY "insert_user_roles" ON user_roles FOR INSERT TO authenticated WITH CHECK (
  EXISTS (SELECT 1 FROM users WHERE users.id = user_roles.user_id AND users.organization_id = (auth.jwt() ->> 'org_id')::uuid)
);
CREATE POLICY "delete_user_roles" ON user_roles FOR DELETE TO authenticated USING (
  EXISTS (SELECT 1 FROM users WHERE users.id = user_roles.user_id AND users.organization_id = (auth.jwt() ->> 'org_id')::uuid)
);

-- Users table
CREATE POLICY "select_users" ON users FOR SELECT TO authenticated USING (organization_id = (auth.jwt() ->> 'org_id')::uuid);
CREATE POLICY "insert_users" ON users FOR INSERT TO authenticated WITH CHECK (organization_id = (auth.jwt() ->> 'org_id')::uuid);
CREATE POLICY "update_users" ON users FOR UPDATE TO authenticated USING (organization_id = (auth.jwt() ->> 'org_id')::uuid) WITH CHECK (organization_id = (auth.jwt() ->> 'org_id')::uuid);
CREATE POLICY "delete_users" ON users FOR DELETE TO authenticated USING (organization_id = (auth.jwt() ->> 'org_id')::uuid);

-- Organizations table
CREATE POLICY "select_organizations" ON organizations FOR SELECT TO authenticated USING (id = (auth.jwt() ->> 'org_id')::uuid);
CREATE POLICY "update_organizations" ON organizations FOR UPDATE TO authenticated USING (id = (auth.jwt() ->> 'org_id')::uuid) WITH CHECK (id = (auth.jwt() ->> 'org_id')::uuid);

-- Audit logs table
CREATE POLICY "select_audit_logs" ON audit_logs FOR SELECT TO authenticated USING (organization_id = (auth.jwt() ->> 'org_id')::uuid);
CREATE POLICY "insert_audit_logs" ON audit_logs FOR INSERT TO authenticated WITH CHECK (organization_id = (auth.jwt() ->> 'org_id')::uuid);

-- Notifications table
CREATE POLICY "select_notifications" ON notifications FOR SELECT TO authenticated USING (organization_id = (auth.jwt() ->> 'org_id')::uuid);
CREATE POLICY "insert_notifications" ON notifications FOR INSERT TO authenticated WITH CHECK (organization_id = (auth.jwt() ->> 'org_id')::uuid);
CREATE POLICY "update_notifications" ON notifications FOR UPDATE TO authenticated USING (organization_id = (auth.jwt() ->> 'org_id')::uuid) WITH CHECK (organization_id = (auth.jwt() ->> 'org_id')::uuid);
CREATE POLICY "delete_notifications" ON notifications FOR DELETE TO authenticated USING (organization_id = (auth.jwt() ->> 'org_id')::uuid);

-- Customers table
CREATE POLICY "select_customers" ON customers FOR SELECT TO authenticated USING (organization_id = (auth.jwt() ->> 'org_id')::uuid);
CREATE POLICY "insert_customers" ON customers FOR INSERT TO authenticated WITH CHECK (organization_id = (auth.jwt() ->> 'org_id')::uuid);
CREATE POLICY "update_customers" ON customers FOR UPDATE TO authenticated USING (organization_id = (auth.jwt() ->> 'org_id')::uuid) WITH CHECK (organization_id = (auth.jwt() ->> 'org_id')::uuid);
CREATE POLICY "delete_customers" ON customers FOR DELETE TO authenticated USING (organization_id = (auth.jwt() ->> 'org_id')::uuid);

-- Drivers table
CREATE POLICY "select_drivers" ON drivers FOR SELECT TO authenticated USING (organization_id = (auth.jwt() ->> 'org_id')::uuid);
CREATE POLICY "insert_drivers" ON drivers FOR INSERT TO authenticated WITH CHECK (organization_id = (auth.jwt() ->> 'org_id')::uuid);
CREATE POLICY "update_drivers" ON drivers FOR UPDATE TO authenticated USING (organization_id = (auth.jwt() ->> 'org_id')::uuid) WITH CHECK (organization_id = (auth.jwt() ->> 'org_id')::uuid);
CREATE POLICY "delete_drivers" ON drivers FOR DELETE TO authenticated USING (organization_id = (auth.jwt() ->> 'org_id')::uuid);

-- Vehicles table
CREATE POLICY "select_vehicles" ON vehicles FOR SELECT TO authenticated USING (organization_id = (auth.jwt() ->> 'org_id')::uuid);
CREATE POLICY "insert_vehicles" ON vehicles FOR INSERT TO authenticated WITH CHECK (organization_id = (auth.jwt() ->> 'org_id')::uuid);
CREATE POLICY "update_vehicles" ON vehicles FOR UPDATE TO authenticated USING (organization_id = (auth.jwt() ->> 'org_id')::uuid) WITH CHECK (organization_id = (auth.jwt() ->> 'org_id')::uuid);
CREATE POLICY "delete_vehicles" ON vehicles FOR DELETE TO authenticated USING (organization_id = (auth.jwt() ->> 'org_id')::uuid);

-- Trip packages table
CREATE POLICY "select_trip_packages" ON trip_packages FOR SELECT TO authenticated USING (organization_id = (auth.jwt() ->> 'org_id')::uuid);
CREATE POLICY "insert_trip_packages" ON trip_packages FOR INSERT TO authenticated WITH CHECK (organization_id = (auth.jwt() ->> 'org_id')::uuid);
CREATE POLICY "update_trip_packages" ON trip_packages FOR UPDATE TO authenticated USING (organization_id = (auth.jwt() ->> 'org_id')::uuid) WITH CHECK (organization_id = (auth.jwt() ->> 'org_id')::uuid);
CREATE POLICY "delete_trip_packages" ON trip_packages FOR DELETE TO authenticated USING (organization_id = (auth.jwt() ->> 'org_id')::uuid);

-- Bookings table
CREATE POLICY "select_bookings" ON bookings FOR SELECT TO authenticated USING (organization_id = (auth.jwt() ->> 'org_id')::uuid);
CREATE POLICY "insert_bookings" ON bookings FOR INSERT TO authenticated WITH CHECK (organization_id = (auth.jwt() ->> 'org_id')::uuid);
CREATE POLICY "update_bookings" ON bookings FOR UPDATE TO authenticated USING (organization_id = (auth.jwt() ->> 'org_id')::uuid) WITH CHECK (organization_id = (auth.jwt() ->> 'org_id')::uuid);
CREATE POLICY "delete_bookings" ON bookings FOR DELETE TO authenticated USING (organization_id = (auth.jwt() ->> 'org_id')::uuid);

-- Trips table
CREATE POLICY "select_trips" ON trips FOR SELECT TO authenticated USING (organization_id = (auth.jwt() ->> 'org_id')::uuid);
CREATE POLICY "insert_trips" ON trips FOR INSERT TO authenticated WITH CHECK (organization_id = (auth.jwt() ->> 'org_id')::uuid);
CREATE POLICY "update_trips" ON trips FOR UPDATE TO authenticated USING (organization_id = (auth.jwt() ->> 'org_id')::uuid) WITH CHECK (organization_id = (auth.jwt() ->> 'org_id')::uuid);
CREATE POLICY "delete_trips" ON trips FOR DELETE TO authenticated USING (organization_id = (auth.jwt() ->> 'org_id')::uuid);

-- Invoices table
CREATE POLICY "select_invoices" ON invoices FOR SELECT TO authenticated USING (organization_id = (auth.jwt() ->> 'org_id')::uuid);
CREATE POLICY "insert_invoices" ON invoices FOR INSERT TO authenticated WITH CHECK (organization_id = (auth.jwt() ->> 'org_id')::uuid);
CREATE POLICY "update_invoices" ON invoices FOR UPDATE TO authenticated USING (organization_id = (auth.jwt() ->> 'org_id')::uuid) WITH CHECK (organization_id = (auth.jwt() ->> 'org_id')::uuid);
CREATE POLICY "delete_invoices" ON invoices FOR DELETE TO authenticated USING (organization_id = (auth.jwt() ->> 'org_id')::uuid);

-- Invoice items table
CREATE POLICY "select_invoice_items" ON invoice_items FOR SELECT TO authenticated USING (organization_id = (auth.jwt() ->> 'org_id')::uuid);
CREATE POLICY "insert_invoice_items" ON invoice_items FOR INSERT TO authenticated WITH CHECK (organization_id = (auth.jwt() ->> 'org_id')::uuid);
CREATE POLICY "update_invoice_items" ON invoice_items FOR UPDATE TO authenticated USING (organization_id = (auth.jwt() ->> 'org_id')::uuid) WITH CHECK (organization_id = (auth.jwt() ->> 'org_id')::uuid);
CREATE POLICY "delete_invoice_items" ON invoice_items FOR DELETE TO authenticated USING (organization_id = (auth.jwt() ->> 'org_id')::uuid);

-- Payments table
CREATE POLICY "select_payments" ON payments FOR SELECT TO authenticated USING (organization_id = (auth.jwt() ->> 'org_id')::uuid);
CREATE POLICY "insert_payments" ON payments FOR INSERT TO authenticated WITH CHECK (organization_id = (auth.jwt() ->> 'org_id')::uuid);
CREATE POLICY "update_payments" ON payments FOR UPDATE TO authenticated USING (organization_id = (auth.jwt() ->> 'org_id')::uuid) WITH CHECK (organization_id = (auth.jwt() ->> 'org_id')::uuid);
CREATE POLICY "delete_payments" ON payments FOR DELETE TO authenticated USING (organization_id = (auth.jwt() ->> 'org_id')::uuid);

-- Expenses table
CREATE POLICY "select_expenses" ON expenses FOR SELECT TO authenticated USING (organization_id = (auth.jwt() ->> 'org_id')::uuid);
CREATE POLICY "insert_expenses" ON expenses FOR INSERT TO authenticated WITH CHECK (organization_id = (auth.jwt() ->> 'org_id')::uuid);
CREATE POLICY "update_expenses" ON expenses FOR UPDATE TO authenticated USING (organization_id = (auth.jwt() ->> 'org_id')::uuid) WITH CHECK (organization_id = (auth.jwt() ->> 'org_id')::uuid);
CREATE POLICY "delete_expenses" ON expenses FOR DELETE TO authenticated USING (organization_id = (auth.jwt() ->> 'org_id')::uuid);

-- Trip profit summary table
CREATE POLICY "select_trip_profit_summary" ON trip_profit_summary FOR SELECT TO authenticated USING (organization_id = (auth.jwt() ->> 'org_id')::uuid);
CREATE POLICY "insert_trip_profit_summary" ON trip_profit_summary FOR INSERT TO authenticated WITH CHECK (organization_id = (auth.jwt() ->> 'org_id')::uuid);
CREATE POLICY "update_trip_profit_summary" ON trip_profit_summary FOR UPDATE TO authenticated USING (organization_id = (auth.jwt() ->> 'org_id')::uuid) WITH CHECK (organization_id = (auth.jwt() ->> 'org_id')::uuid);
CREATE POLICY "delete_trip_profit_summary" ON trip_profit_summary FOR DELETE TO authenticated USING (organization_id = (auth.jwt() ->> 'org_id')::uuid);

-- Vehicle daily profit table
CREATE POLICY "select_vehicle_daily_profit" ON vehicle_daily_profit FOR SELECT TO authenticated USING (organization_id = (auth.jwt() ->> 'org_id')::uuid);
CREATE POLICY "insert_vehicle_daily_profit" ON vehicle_daily_profit FOR INSERT TO authenticated WITH CHECK (organization_id = (auth.jwt() ->> 'org_id')::uuid);
CREATE POLICY "update_vehicle_daily_profit" ON vehicle_daily_profit FOR UPDATE TO authenticated USING (organization_id = (auth.jwt() ->> 'org_id')::uuid) WITH CHECK (organization_id = (auth.jwt() ->> 'org_id')::uuid);
CREATE POLICY "delete_vehicle_daily_profit" ON vehicle_daily_profit FOR DELETE TO authenticated USING (organization_id = (auth.jwt() ->> 'org_id')::uuid);

-- Vehicle monthly profit table
CREATE POLICY "select_vehicle_monthly_profit" ON vehicle_monthly_profit FOR SELECT TO authenticated USING (organization_id = (auth.jwt() ->> 'org_id')::uuid);
CREATE POLICY "insert_vehicle_monthly_profit" ON vehicle_monthly_profit FOR INSERT TO authenticated WITH CHECK (organization_id = (auth.jwt() ->> 'org_id')::uuid);
CREATE POLICY "update_vehicle_monthly_profit" ON vehicle_monthly_profit FOR UPDATE TO authenticated USING (organization_id = (auth.jwt() ->> 'org_id')::uuid) WITH CHECK (organization_id = (auth.jwt() ->> 'org_id')::uuid);
CREATE POLICY "delete_vehicle_monthly_profit" ON vehicle_monthly_profit FOR DELETE TO authenticated USING (organization_id = (auth.jwt() ->> 'org_id')::uuid);

-- Maintenance schedule table
CREATE POLICY "select_maintenance_schedule" ON maintenance_schedule FOR SELECT TO authenticated USING (organization_id = (auth.jwt() ->> 'org_id')::uuid);
CREATE POLICY "insert_maintenance_schedule" ON maintenance_schedule FOR INSERT TO authenticated WITH CHECK (organization_id = (auth.jwt() ->> 'org_id')::uuid);
CREATE POLICY "update_maintenance_schedule" ON maintenance_schedule FOR UPDATE TO authenticated USING (organization_id = (auth.jwt() ->> 'org_id')::uuid) WITH CHECK (organization_id = (auth.jwt() ->> 'org_id')::uuid);
CREATE POLICY "delete_maintenance_schedule" ON maintenance_schedule FOR DELETE TO authenticated USING (organization_id = (auth.jwt() ->> 'org_id')::uuid);

-- Vehicle calendar events table
CREATE POLICY "select_vehicle_calendar_events" ON vehicle_calendar_events FOR SELECT TO authenticated USING (organization_id = (auth.jwt() ->> 'org_id')::uuid);
CREATE POLICY "insert_vehicle_calendar_events" ON vehicle_calendar_events FOR INSERT TO authenticated WITH CHECK (organization_id = (auth.jwt() ->> 'org_id')::uuid);
CREATE POLICY "update_vehicle_calendar_events" ON vehicle_calendar_events FOR UPDATE TO authenticated USING (organization_id = (auth.jwt() ->> 'org_id')::uuid) WITH CHECK (organization_id = (auth.jwt() ->> 'org_id')::uuid);
CREATE POLICY "delete_vehicle_calendar_events" ON vehicle_calendar_events FOR DELETE TO authenticated USING (organization_id = (auth.jwt() ->> 'org_id')::uuid);

-- Reminder rules table
CREATE POLICY "select_reminder_rules" ON reminder_rules FOR SELECT TO authenticated USING (organization_id = (auth.jwt() ->> 'org_id')::uuid);
CREATE POLICY "insert_reminder_rules" ON reminder_rules FOR INSERT TO authenticated WITH CHECK (organization_id = (auth.jwt() ->> 'org_id')::uuid);
CREATE POLICY "update_reminder_rules" ON reminder_rules FOR UPDATE TO authenticated USING (organization_id = (auth.jwt() ->> 'org_id')::uuid) WITH CHECK (organization_id = (auth.jwt() ->> 'org_id')::uuid);
CREATE POLICY "delete_reminder_rules" ON reminder_rules FOR DELETE TO authenticated USING (organization_id = (auth.jwt() ->> 'org_id')::uuid);

-- Reminders table
CREATE POLICY "select_reminders" ON reminders FOR SELECT TO authenticated USING (organization_id = (auth.jwt() ->> 'org_id')::uuid);
CREATE POLICY "insert_reminders" ON reminders FOR INSERT TO authenticated WITH CHECK (organization_id = (auth.jwt() ->> 'org_id')::uuid);
CREATE POLICY "update_reminders" ON reminders FOR UPDATE TO authenticated USING (organization_id = (auth.jwt() ->> 'org_id')::uuid) WITH CHECK (organization_id = (auth.jwt() ->> 'org_id')::uuid);
CREATE POLICY "delete_reminders" ON reminders FOR DELETE TO authenticated USING (organization_id = (auth.jwt() ->> 'org_id')::uuid);

-- Notification events table
CREATE POLICY "select_notification_events" ON notification_events FOR SELECT TO authenticated USING (organization_id = (auth.jwt() ->> 'org_id')::uuid);
CREATE POLICY "insert_notification_events" ON notification_events FOR INSERT TO authenticated WITH CHECK (organization_id = (auth.jwt() ->> 'org_id')::uuid);
CREATE POLICY "update_notification_events" ON notification_events FOR UPDATE TO authenticated USING (organization_id = (auth.jwt() ->> 'org_id')::uuid) WITH CHECK (organization_id = (auth.jwt() ->> 'org_id')::uuid);
CREATE POLICY "delete_notification_events" ON notification_events FOR DELETE TO authenticated USING (organization_id = (auth.jwt() ->> 'org_id')::uuid);

-- Notification preferences table
CREATE POLICY "select_notification_preferences" ON notification_preferences FOR SELECT TO authenticated USING (organization_id = (auth.jwt() ->> 'org_id')::uuid);
CREATE POLICY "insert_notification_preferences" ON notification_preferences FOR INSERT TO authenticated WITH CHECK (organization_id = (auth.jwt() ->> 'org_id')::uuid);
CREATE POLICY "update_notification_preferences" ON notification_preferences FOR UPDATE TO authenticated USING (organization_id = (auth.jwt() ->> 'org_id')::uuid) WITH CHECK (organization_id = (auth.jwt() ->> 'org_id')::uuid);
CREATE POLICY "delete_notification_preferences" ON notification_preferences FOR DELETE TO authenticated USING (organization_id = (auth.jwt() ->> 'org_id')::uuid);