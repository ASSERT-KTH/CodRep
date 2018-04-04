throw new UnavailableException("Testing ", 10);

import javax.servlet.*;
import javax.servlet.http.*;
import java.io.*;

public class Unavailable extends HttpServlet {
    static int attempt=0;
    
    public void init(ServletConfig conf)
        throws ServletException
    {
	System.out.println("Try to init ");
	attempt++;
	if( attempt < 2 ) 
	    throw new UnavailableException( 10, this, "Testing " );
	System.out.println("Init ok ");
    }

    public void service(HttpServletRequest req, HttpServletResponse res)
        throws IOException
    {
        res.setContentType("text/plain");

        ServletOutputStream out = res.getOutputStream();

	out.println("Hello");

        out.close();
    }
}
