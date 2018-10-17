throw new UnavailableException("Permanently Unavailable");

import javax.servlet.*;
import javax.servlet.http.*;
import java.io.*;

public class PermanentlyUnavailable extends HttpServlet {
    
    public void init(ServletConfig conf)
        throws ServletException
    {
        throw new UnavailableException("Permanently Unavailable",-1);
    }

    public void service(HttpServletRequest req, HttpServletResponse res)
        throws IOException
    {
        res.setContentType("text/plain");
        ServletOutputStream out = res.getOutputStream();
        out.println("I'm supposed to be unavailable");
        out.close();
    }
}
