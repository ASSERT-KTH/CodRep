protected int executeInsert(int paramIndex, PreparedStatement ps, EntityEnterpriseContext ctx ) throws SQLException {

/***************************************
 *                                     *
 *  JBoss: The OpenSource J2EE WebOS   *
 *                                     *
 *  Distributable under LGPL license.  *
 *  See terms of license at gnu.org.   *
 *                                     *
 ***************************************/
package org.jboss.ejb.plugins.cmp.jdbc.keygen;

import java.sql.Connection;
import java.sql.PreparedStatement;
import java.sql.ResultSet;
import java.sql.SQLException;
import javax.ejb.EJBException;
import org.jboss.ejb.EntityEnterpriseContext;
import org.jboss.ejb.plugins.cmp.jdbc.JDBCIdentityColumnCreateCommand;
import org.jboss.ejb.plugins.cmp.jdbc.JDBCUtil;

/**
 * Create method that uses the identity_val_local() function in DB2 to get
 * get the ID of the last inserted row, and populate it into the EJB
 * object being created.
 *
 * @author <a href="mailto:dwintschel@esports.com">Daniel Wintschel</a>
 */
public class JDBCDB2IdentityValLocalCreateCommand extends JDBCIdentityColumnCreateCommand {
    private static final String SQL = "values (identity_val_local())";

    protected int executeInsert( PreparedStatement ps, EntityEnterpriseContext ctx ) throws SQLException {
        int rows = ps.executeUpdate();
        ResultSet results = null;
        try {
            Connection conn = ps.getConnection();
            results = conn.prepareStatement( SQL ).executeQuery();
            if( !results.next() ) {
                throw new EJBException( "identity_val_local() returned an empty ResultSet" );
            }
            pkField.loadInstanceResults( results, 1, ctx );
        } catch( RuntimeException e ) {
            throw e;
        } catch( Exception e ) {
            // throw EJBException to force a rollback as the row has been inserted
            throw new EJBException( "Error extracting identity_val_local()", e );
        } finally {
            JDBCUtil.safeClose( results );
        }
        return rows;
    }
}