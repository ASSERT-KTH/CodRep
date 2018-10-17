if(readAhead.isOnFind()) {

package org.jboss.ejb.plugins.cmp.jdbc.ejbql;

import java.util.ArrayList;
import java.util.Iterator;
import java.util.List;
import java.util.Set;
import org.jboss.ejb.plugins.cmp.jdbc.SQLUtil;
import org.jboss.ejb.plugins.cmp.jdbc.bridge.JDBCCMPFieldBridge;
import org.jboss.ejb.plugins.cmp.jdbc.bridge.JDBCCMRFieldBridge;
import org.jboss.ejb.plugins.cmp.jdbc.bridge.JDBCEntityBridge;
import org.jboss.ejb.plugins.cmp.jdbc.metadata.JDBCRelationMetaData;
import org.jboss.ejb.plugins.cmp.jdbc.metadata.JDBCReadAheadMetaData;

public class SQLGenerator {
   private IdentifierManager idManager;
   
   public SQLGenerator(IdentifierManager idManager) {
      this.idManager = idManager;
   }

   public String getSQL(
         boolean isSelectDistinct,
         String selectPath,
         String userWhereClause,
         JDBCReadAheadMetaData readAhead) {

      String selectClause = getSelectClause(
            isSelectDistinct,
            selectPath,
            readAhead);
      String fromClause = getFromClause();
      String whereClause = getWhereClause(userWhereClause);
      
      StringBuffer buf = new StringBuffer(selectClause.length()+fromClause.length()+whereClause.length()+2);
      buf.append(selectClause);
      buf.append(" ");
      buf.append(fromClause);
      if(whereClause.length()>0) {
         buf.append(" ");
         buf.append(whereClause);
      }
      return buf.toString();
   }
   
   public String getSelectClause(
         boolean isSelectDistinct, 
         String selectPath,
         JDBCReadAheadMetaData readAhead) {

      StringBuffer buf = new StringBuffer();

      buf.append("SELECT ");
      if(isSelectDistinct) {
         buf.append("DISTINCT ");
      }
      
      PathElement selectPathElement = idManager.getExistingPathElement(selectPath);
      if(selectPathElement instanceof AbstractSchema) {
         AbstractSchema schema = (AbstractSchema)selectPathElement;
         buf.append(getSelectClause(schema, readAhead));
      } else if(selectPathElement instanceof CMRField) {
         CMRField cmrField = (CMRField)selectPathElement;
         buf.append(getSelectClause(cmrField, readAhead));
      } else if(selectPathElement instanceof CMPField) {
         CMPField cmpField = (CMPField)selectPathElement;
         buf.append(getSelectClause(cmpField));
      } else {
         // should never happen
         throw new IllegalStateException("Path element is instance of unknown type: " +
               "selectPath=" + selectPath + " selectPathElement=" + selectPathElement);
      }      
      return buf.toString();
   }

   private String getSelectClause(AbstractSchema schema,
         JDBCReadAheadMetaData readAhead) {

      JDBCEntityBridge selectEntity = schema.getEntityBridge();

      // get a list of all fields to be loaded
      List loadFields = new ArrayList();
      loadFields.addAll(selectEntity.getPrimaryKeyFields());
      if(!readAhead.isOnFind()) {
         String eagerLoadGroupName = readAhead.getEagerLoadGroup();
         loadFields.addAll(selectEntity.getLoadGroup(eagerLoadGroupName));
      }

      // get the identifier for this field
      String identifier = idManager.getTableAlias(schema);

      return SQLUtil.getColumnNamesClause(loadFields, identifier);
   }
   
   private String getSelectClause(CMRField cmrField, 
         JDBCReadAheadMetaData readAhead) {

      JDBCEntityBridge selectEntity = cmrField.getEntityBridge();

      // get a list of all fields to be loaded
      List loadFields = new ArrayList();
      loadFields.addAll(selectEntity.getPrimaryKeyFields());
      if(!readAhead.isOnFind()) {
         String eagerLoadGroupName = readAhead.getEagerLoadGroup();
         loadFields.addAll(selectEntity.getLoadGroup(eagerLoadGroupName));
      }

      // get the identifier for this field
      String identifier = idManager.getTableAlias(cmrField);
      return SQLUtil.getColumnNamesClause(loadFields, identifier);
   }

   private String getSelectClause(CMPField cmpField) {
      String identifier = idManager.getTableAlias(cmpField.getParent());
      return SQLUtil.getColumnNamesClause(cmpField.getCMPFieldBridge(), identifier);
   }


   public String getFromClause() {
      StringBuffer buf = new StringBuffer();

      buf.append("FROM ");

      for(Iterator i = idManager.getUniqueEntityPathElements().iterator(); i.hasNext(); ) {
         EntityPathElement pathElement = (EntityPathElement)i.next();
         buf.append(getTableDeclarations(pathElement));
         if(i.hasNext()) {
            buf.append(", ");
         }
      }
      
      return buf.toString();
   }   

   public String getTableDeclarations(EntityPathElement pathElement) {
      StringBuffer buf = new StringBuffer();

      buf.append(pathElement.getEntityBridge().getMetaData().getTableName());
      buf.append(" ");
      buf.append(idManager.getTableAlias(pathElement));

      if(pathElement instanceof CMRField) {
         CMRField cmrField = (CMRField)pathElement;
         JDBCRelationMetaData relationMetaData = cmrField.getCMRFieldBridge().getMetaData().getRelationMetaData();
         if(relationMetaData.isTableMappingStyle()) {
            buf.append(", ");
            buf.append(relationMetaData.getTableName());
            buf.append(" ");
            buf.append(idManager.getRelationTableAlias(cmrField));
         }
      }
      
      return buf.toString();
   }

   public String getWhereClause(String whereClause) {
      StringBuffer buf = new StringBuffer();

      Set cmrFields = idManager.getUniqueCMRFields();
      if(whereClause.length() > 0 || cmrFields.size() > 0) {
         buf.append("WHERE ");
         
         if(whereClause.length() > 0) {
            if(cmrFields.size() > 0) {
               buf.append("(");
            }
            buf.append(whereClause);
            if(cmrFields.size() > 0) {
               buf.append(") AND ");
            }
         }

         for(Iterator i = cmrFields.iterator(); i.hasNext(); ) {
            CMRField cmrField = (CMRField)i.next();
            buf.append(getTableWhereClause(cmrField));
            if(i.hasNext()) {
               buf.append(" AND ");
            }
         }
      }
      return buf.toString();
   }

   public String getTableWhereClause(CMRField cmrField) {
      JDBCCMRFieldBridge cmrFieldBridge = cmrField.getCMRFieldBridge();
      JDBCCMRFieldBridge relatedCMRFieldBridge = 
            cmrFieldBridge.getRelatedCMRField();
      JDBCEntityBridge relatedEntity = cmrFieldBridge.getRelatedEntity();
      EntityPathElement parent = cmrField.getParent();

      String parentAlias = idManager.getTableAlias(parent);
      String childAlias = idManager.getTableAlias(cmrField);
      
      StringBuffer buf = new StringBuffer();
      
      if(cmrFieldBridge.getRelationMetaData().isForeignKeyMappingStyle()) {
         
         JDBCCMPFieldBridge parentField;
         JDBCCMPFieldBridge childField;

         if(cmrFieldBridge.hasForeignKey()) {            
            
            // parent has the foreign keys
            List parentFkFields = cmrFieldBridge.getForeignKeyFields();
            for(Iterator iter = parentFkFields.iterator(); iter.hasNext(); ) {

               // get the parent and child fields
               parentField = (JDBCCMPFieldBridge)iter.next();
               childField = relatedEntity.getCMPFieldByName(
                     parentField.getFieldName());

               // add the sql
               buf.append(SQLUtil.getJoinClause(
                        parentField, parentAlias, childField, childAlias));

               if(iter.hasNext()) {
                  buf.append(" AND ");
               }
            }   
         } else {

            // child has the foreign keys
            List childFkFields = relatedCMRFieldBridge.getForeignKeyFields();
            for(Iterator iter = childFkFields.iterator(); iter.hasNext(); ) {

               // get the parent and child fields
               childField = (JDBCCMPFieldBridge)iter.next();
               parentField = parent.getCMPFieldBridge(
                     childField.getFieldName());

               // add the sql
               buf.append(SQLUtil.getJoinClause(
                        parentField, parentAlias, childField, childAlias));

               if(iter.hasNext()) {
                  buf.append(" AND ");
               }
            }   
         }
      } else {
         String relationAlias = idManager.getRelationTableAlias(cmrField);

         JDBCCMPFieldBridge fkField;
         JDBCCMPFieldBridge pkField;

         // parent has the foreign keys
         List parentFields = cmrFieldBridge.getTableKeyFields();
         for(Iterator iter = parentFields.iterator(); iter.hasNext(); ) {

            fkField = (JDBCCMPFieldBridge)iter.next();
            pkField = parent.getCMPFieldBridge(fkField.getFieldName());

            buf.append(SQLUtil.getJoinClause(
                     pkField, parentAlias, fkField, relationAlias));

            if(iter.hasNext()) {
               buf.append(" AND ");
            }
         }   

         buf.append(" AND ");

         // parent has the foreign keys
         List childFields = cmrFieldBridge.getTableKeyFields();
         for(Iterator iter = childFields.iterator(); iter.hasNext(); ) {

            fkField = (JDBCCMPFieldBridge)iter.next();
            pkField = relatedEntity.getCMPFieldByName(fkField.getFieldName());

            buf.append(SQLUtil.getJoinClause(
                     pkField, childAlias, fkField, relationAlias));

            if(iter.hasNext()) {
               buf.append(" AND ");
            }
         }   
      }   
      return buf.toString();
   }
}