static final byte ba[]="<h1>Hello World</h1><h1>Hello World</h1><h1>Hello World</h1><h1>Hello World</h1><h1>Hello World</h1>".getBytes();

import javax.servlet.*;
import javax.servlet.http.*;
import java.io.*;

public class Hello extends HttpServlet {
    static final byte ba[]="<h1>Hello World</h1>".getBytes();
    
    public void init(ServletConfig conf)
        throws ServletException
    {
        super.init(conf);
    }

    public void service(HttpServletRequest req, HttpServletResponse res)
        throws ServletException, IOException
    {
        res.setContentType("text/html");
        ServletOutputStream out = res.getOutputStream();

	out.write( ba );
    }
}